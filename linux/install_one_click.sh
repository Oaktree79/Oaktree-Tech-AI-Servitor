#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "AI Serviter One-Click Installer"
PYTHON="python3"
if [ -x "$ROOT/installer/runtime/python/bin/python3" ]; then
  PYTHON="$ROOT/installer/runtime/python/bin/python3"
fi

"$PYTHON" -m venv .venv
"$ROOT/.venv/bin/python" -m pip install -U pip
"$ROOT/.venv/bin/python" -m pip install -e "$ROOT/python[dev]"
"$ROOT/.venv/bin/python" -m ai_serviter.one_click --root "$ROOT" setup
"$ROOT/.venv/bin/python" -m ai_serviter.one_click --root "$ROOT" launch

echo "AI Serviter installed and launched."
