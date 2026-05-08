from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import shutil
import subprocess


class KubernetesDeploymentTester:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def status(self) -> Dict:
        return {
            "kubectl_available": shutil.which("kubectl") is not None,
            "helm_available": shutil.which("helm") is not None,
        }

    def validate_yaml(self, path: str | Path) -> Dict:
        path = Path(path)
        if shutil.which("kubectl") is None:
            return {"ok": False, "reason": "kubectl not installed", "path": str(path)}
        proc = subprocess.run(
            ["kubectl", "apply", "--dry-run=client", "-f", str(path)],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )
        return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr, "path": str(path)}

    def helm_lint(self, chart_path: str | Path) -> Dict:
        if shutil.which("helm") is None:
            return {"ok": False, "reason": "helm not installed", "chart": str(chart_path)}
        proc = subprocess.run(["helm", "lint", str(chart_path)], cwd=self.root, capture_output=True, text=True, check=False)
        return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr, "chart": str(chart_path)}
