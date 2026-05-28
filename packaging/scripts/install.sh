#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="${1:-/tmp/hermes-agent}"
INSTALL_DIR=/opt/hermes-agent
CONFIG_DIR=/etc/hermes-agent
STATE_DIR=/var/lib/hermes-agent

dnf install -y python3 python3-pip wget rsync shadow-utils policycoreutils-python-utils

if ! getent group hermes >/dev/null; then
  groupadd --system hermes
fi
if ! id hermes >/dev/null 2>&1; then
  useradd --system --gid hermes --home-dir "${STATE_DIR}" --shell /sbin/nologin hermes
fi

install -d -m 0755 "${INSTALL_DIR}"
install -d -m 0770 -o root -g hermes "${CONFIG_DIR}" "${STATE_DIR}"

rsync -a --delete \
  --exclude ".git" \
  --exclude ".venv" \
  --exclude "__pycache__" \
  "${SOURCE_DIR}/" "${INSTALL_DIR}/"

python3 -m venv "${INSTALL_DIR}/.venv"
"${INSTALL_DIR}/.venv/bin/python" -m pip install --upgrade pip
"${INSTALL_DIR}/.venv/bin/python" -m pip install -r "${INSTALL_DIR}/requirements.txt"

install -m 0644 "${INSTALL_DIR}/packaging/systemd/hermes-agent.service" /etc/systemd/system/hermes-agent.service
install -m 0644 "${INSTALL_DIR}/packaging/systemd/hermes-agent-firstboot.service" /etc/systemd/system/hermes-agent-firstboot.service
install -m 0755 "${INSTALL_DIR}/packaging/scripts/hermes-agent-firstboot" /usr/local/sbin/hermes-agent-firstboot
install -m 0755 "${INSTALL_DIR}/packaging/scripts/hermes-agent-ctl" /usr/local/bin/hermes-agent-ctl

if command -v semanage >/dev/null 2>&1; then
  semanage port -a -t http_port_t -p tcp 8080 2>/dev/null || semanage port -m -t http_port_t -p tcp 8080
fi

systemctl daemon-reload
systemctl enable hermes-agent-firstboot.service
systemctl enable hermes-agent.service

echo "Hermes Agent installed into ${INSTALL_DIR}"
