#!/usr/bin/env bash
set -euo pipefail

rm -f /etc/hermes-agent/setup-token
rm -f /etc/hermes-agent/aws-sdk.env
rm -f /etc/hermes-agent/config.json
rm -f /root/.ssh/authorized_keys
rm -f /home/*/.ssh/authorized_keys 2>/dev/null || true
rm -f /etc/ssh/ssh_host_*

find /var/log -type f -exec truncate -s 0 {} \; 2>/dev/null || true
rm -rf /tmp/* /var/tmp/*
rm -f /root/.bash_history /home/*/.bash_history 2>/dev/null || true

dnf clean all || true
cloud-init clean --logs || true

sync
