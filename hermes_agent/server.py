from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
import argparse
import json
import mimetypes
import os
import secrets
import sys
import traceback

from . import __version__
from .bedrock import converse
from .config import DEFAULT_CONFIG_PATH, HermesConfig, load_config, save_config


STATIC_DIR = Path(__file__).with_name("static")
TOKEN_FILE = Path(os.environ.get("HERMES_AGENT_TOKEN_FILE", "/etc/hermes-agent/setup-token"))


class RuntimeState:
    def __init__(self, config_path: Path, token_file: Path) -> None:
        self.config_path = config_path
        self.token_file = token_file

    def load_config(self) -> HermesConfig:
        return load_config(self.config_path)

    def save_config(self, config: HermesConfig) -> None:
        save_config(config, self.config_path)

    def token(self) -> str | None:
        try:
            token = self.token_file.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            token = os.environ.get("HERMES_AGENT_TOKEN", "").strip()
        return token or None


class HermesHandler(BaseHTTPRequestHandler):
    server_version = f"HermesAgent/{__version__}"

    @property
    def state(self) -> RuntimeState:
        return self.server.state  # type: ignore[attr-defined]

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), fmt % args))

    def do_GET(self) -> None:
        if self.path == "/api/health":
            config = self.state.load_config()
            self.send_json(
                {
                    "ok": True,
                    "version": __version__,
                    "initialized": config.initialized,
                    "auth_required": self.state.token() is not None,
                }
            )
            return
        if self.path == "/api/config":
            if not self.authorized():
                return
            self.send_json(self.state.load_config().public_dict())
            return
        self.serve_static()

    def do_PUT(self) -> None:
        if self.path != "/api/config":
            self.send_error_json(HTTPStatus.NOT_FOUND, "Route not found")
            return
        if not self.authorized():
            return
        payload = self.read_json()
        current = self.state.load_config()
        updated = current.update_from(payload)
        updated.initialized = True
        self.state.save_config(updated)
        self.send_json(updated.public_dict())

    def do_POST(self) -> None:
        if not self.authorized():
            return
        if self.path == "/api/chat":
            payload = self.read_json()
            message = str(payload.get("message", "")).strip()
            if not message:
                self.send_error_json(HTTPStatus.BAD_REQUEST, "Message is required")
                return
            result = converse(self.state.load_config(), message)
            self.send_json(result)
            return
        if self.path == "/api/test":
            result = converse(self.state.load_config(), "Reply with a short readiness confirmation.")
            self.send_json(result)
            return
        self.send_error_json(HTTPStatus.NOT_FOUND, "Route not found")

    def authorized(self) -> bool:
        expected = self.state.token()
        if expected is None:
            return True
        header = self.headers.get("X-Hermes-Token") or self.headers.get("Authorization") or ""
        supplied = header.removeprefix("Bearer ").strip()
        if secrets.compare_digest(expected, supplied):
            return True
        self.send_error_json(HTTPStatus.UNAUTHORIZED, "Valid setup token is required")
        return False

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON request body") from exc
        if not isinstance(payload, dict):
            raise ValueError("JSON request body must be an object")
        return payload

    def serve_static(self) -> None:
        relative = self.path.split("?", 1)[0].lstrip("/") or "index.html"
        if relative.startswith("assets/"):
            relative = relative.removeprefix("assets/")
        target = (STATIC_DIR / relative).resolve()
        if STATIC_DIR.resolve() not in target.parents and target != STATIC_DIR.resolve():
            self.send_error_json(HTTPStatus.FORBIDDEN, "Forbidden")
            return
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            target = STATIC_DIR / "index.html"
        content_type, _ = mimetypes.guess_type(target)
        data = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store" if target.name == "index.html" else "public, max-age=3600")
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_error_json(self, status: HTTPStatus, message: str) -> None:
        self.send_json({"ok": False, "error": message}, status)

    def handle_one_request(self) -> None:
        try:
            super().handle_one_request()
        except Exception as exc:
            traceback.print_exc()
            if not self.wfile.closed:
                self.send_error_json(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


class HermesServer(ThreadingHTTPServer):
    def __init__(self, address: tuple[str, int], handler: type[BaseHTTPRequestHandler], state: RuntimeState) -> None:
        super().__init__(address, handler)
        self.state = state


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Hermes Agent Web UI")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH))
    parser.add_argument("--token-file", default=str(TOKEN_FILE))
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", default=None, type=int)
    args = parser.parse_args()

    state = RuntimeState(Path(args.config), Path(args.token_file))
    config = state.load_config()
    host = args.host or config.bind_host
    port = args.port or config.bind_port
    httpd = HermesServer((host, port), HermesHandler, state)
    print(f"Hermes Agent {__version__} listening on http://{host}:{port}", flush=True)
    httpd.serve_forever()
