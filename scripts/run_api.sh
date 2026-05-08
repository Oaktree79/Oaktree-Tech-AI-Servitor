#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../python"
python -m pip install -e ".[dev]"
export SERVITER_ADMIN_PASSWORD="${SERVITER_ADMIN_PASSWORD:-admin-change-me}"
serviter-service --root . --mode api --host 127.0.0.1 --port 8765
