#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="$ROOT/installer/assets/ai-serviter-logo.svg"
OUT="$ROOT/installer/branding"
mkdir -p "$OUT"
if command -v magick >/dev/null 2>&1; then
  magick "$SRC" "$OUT/ai-serviter.ico"
  magick "$SRC" "$OUT/ai-serviter.png"
else
  echo "ImageMagick not found."
fi
