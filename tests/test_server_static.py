from pathlib import Path

from hermes_agent.server import HermesHandler


def test_index_asset_paths_work_when_opened_as_file():
    html = Path("hermes_agent/static/index.html").read_text(encoding="utf-8")

    assert 'href="./styles.css"' in html
    assert '<span class="brand-text">VSTECS</span>' in html
    assert 'data-section="aws-section"' in html
    assert "vstecs-logo.png" not in html
    assert 'src="./app.js"' in html


def test_static_root_paths_resolve_for_relative_index_references():
    assert HermesHandler.resolve_static_target(None, "styles.css") == Path("hermes_agent/static/styles.css").resolve()
    assert HermesHandler.resolve_static_target(None, "app.js") == Path("hermes_agent/static/app.js").resolve()


def test_legacy_asset_paths_still_resolve_static_root_files():
    target = HermesHandler.resolve_static_target(None, "assets/styles.css")

    assert target == Path("hermes_agent/static/styles.css").resolve()
