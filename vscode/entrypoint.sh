#!/usr/bin/env bash
set -euo pipefail

mkdir -p /home/coder/.vscode-server-data /home/coder/projects
chown -R coder:coder /home/coder/.vscode-server-data /home/coder/projects

exec gosu coder code serve-web \
    --host 0.0.0.0 \
    --port 8000 \
    --server-data-dir /home/coder/.vscode-server-data \
    --accept-server-license-terms \
    --without-connection-token
