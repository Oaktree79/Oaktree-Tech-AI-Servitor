#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-python}"
STAMP="$(date +%Y%m%d-%H%M%S)"
mkdir -p backups
tar -czf "backups/serviter-$STAMP.tar.gz" "$ROOT/.serviter" 2>/dev/null || true
echo "backup written: backups/serviter-$STAMP.tar.gz"
