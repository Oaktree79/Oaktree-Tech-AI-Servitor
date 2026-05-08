#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "[trial] validating docker compose config"
docker compose -f deploy/docker/docker-compose.yml config
echo "[trial] building docker image"
docker build -f deploy/docker/Dockerfile -t ai-serviter:trial .
echo "[trial] docker validation completed"
