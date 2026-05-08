from __future__ import annotations

from pathlib import Path
from typing import Dict
import shutil
import subprocess

from .path_resolver import ProjectRootResolver


class DeploymentValidator:
    def __init__(self, root: str | Path):
        self.input_root = Path(root).resolve()
        self.root = ProjectRootResolver(root).resolve()

    def docker_compose_config(self, compose_file: str | Path = "deploy/docker/docker-compose.yml") -> Dict:
        compose_path = self.root / compose_file
        if not compose_path.exists():
            return {"ok": False, "reason": "compose file missing", "file": str(compose_path), "resolved_root": str(self.root)}
        if shutil.which("docker") is None:
            return {"ok": False, "reason": "docker not installed", "file": str(compose_path), "resolved_root": str(self.root)}
        proc = subprocess.run(
            ["docker", "compose", "-f", str(compose_path), "config"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr, "resolved_root": str(self.root)}

    def kubernetes_dry_run(self, manifest: str | Path = "deploy/k8s/deployment.yaml") -> Dict:
        manifest_path = self.root / manifest
        if not manifest_path.exists():
            return {"ok": False, "reason": "manifest missing", "file": str(manifest_path), "resolved_root": str(self.root)}
        if shutil.which("kubectl") is None:
            return {"ok": False, "reason": "kubectl not installed", "file": str(manifest_path), "resolved_root": str(self.root)}
        proc = subprocess.run(
            ["kubectl", "apply", "--dry-run=client", "-f", str(manifest_path)],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr, "resolved_root": str(self.root)}

    def validate_files_present(self) -> Dict:
        required = [
            "deploy/docker/Dockerfile",
            "deploy/docker/docker-compose.yml",
            "deploy/k8s/deployment.yaml",
            "python/pyproject.toml",
        ]
        missing = [p for p in required if not (self.root / p).exists()]
        return {"ok": not missing, "missing": missing, "resolved_root": str(self.root), "input_root": str(self.input_root)}
