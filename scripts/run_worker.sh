#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../python"
python -m pip install -e ".[dev]"
serviter-service --root . --mode worker --interval 2
