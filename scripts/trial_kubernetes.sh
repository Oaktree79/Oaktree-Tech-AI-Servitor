#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "[trial] kubernetes client-side dry run"
kubectl apply --dry-run=client -f deploy/k8s/deployment.yaml
echo "[trial] kubernetes validation completed"
