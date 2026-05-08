from __future__ import annotations

from pathlib import Path
from typing import Dict
import shutil
import subprocess

from .defaults_scanner import DefaultsScanner
from .network_policy import NetworkPolicy
from .security_hardening import SecurityHardeningChecker


class SecurityReviewToolkit:
    """
    Aggregates security review checks for a release candidate.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def run(self) -> Dict:
        return {
            "defaults_files": DefaultsScanner(self.root).scan_files(),
            "defaults_environment": DefaultsScanner(self.root).scan_environment(),
            "hardening": SecurityHardeningChecker(self.root).check(),
            "network_policy_sample": {
                "metadata": NetworkPolicy().check_url("http://169.254.169.254/latest/meta-data"),
                "github": NetworkPolicy().check_url("https://github.com"),
            },
            "dependency_tools": self.dependency_tools_status(),
        }

    def dependency_tools_status(self) -> Dict:
        return {
            "pip_audit_available": shutil.which("pip-audit") is not None,
            "trivy_available": shutil.which("trivy") is not None,
            "bandit_available": shutil.which("bandit") is not None,
        }

    def run_optional_pip_audit(self) -> Dict:
        if shutil.which("pip-audit") is None:
            return {"ok": False, "reason": "pip-audit not installed"}
        proc = subprocess.run(["pip-audit"], cwd=self.root / "python", capture_output=True, text=True, check=False)
        return {"ok": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr}
