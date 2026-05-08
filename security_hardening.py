from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import os
import stat


class SecurityHardeningChecker:
    """
    Checks common production hardening requirements.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def check(self) -> Dict:
        checks = [
            self.check_secret_env(),
            self.check_dev_password(),
            self.check_file_permissions(),
            self.check_tls_hint(),
            self.check_docker_hardening(),
        ]
        return {
            "ok": all(c["ok"] for c in checks),
            "checks": checks,
        }

    def check_secret_env(self) -> Dict:
        secret = os.getenv("SERVITER_SECRET", "")
        return {
            "name": "SERVITER_SECRET",
            "ok": bool(secret and secret != "change-this-secret" and len(secret) >= 24),
            "message": "SERVITER_SECRET should be a long random value.",
        }

    def check_dev_password(self) -> Dict:
        password = os.getenv("SERVITER_ADMIN_PASSWORD", "")
        return {
            "name": "SERVITER_ADMIN_PASSWORD",
            "ok": bool(password and password not in {"change-me", "admin-change-me", "password"}),
            "message": "Admin password must be changed from development defaults.",
        }

    def check_file_permissions(self) -> Dict:
        serviter_dir = self.root / ".serviter"
        if not serviter_dir.exists():
            return {"name": "file_permissions", "ok": True, "message": ".serviter not created yet."}
        mode = stat.S_IMODE(serviter_dir.stat().st_mode)
        return {
            "name": "file_permissions",
            "ok": mode & 0o077 == 0,
            "message": ".serviter should not be group/world readable in production.",
            "mode": oct(mode),
        }

    def check_tls_hint(self) -> Dict:
        return {
            "name": "tls",
            "ok": bool(os.getenv("SERVITER_TLS_TERMINATED", "")),
            "message": "Set SERVITER_TLS_TERMINATED=1 when running behind HTTPS/TLS reverse proxy.",
        }

    def check_docker_hardening(self) -> Dict:
        dockerfile = self.root / "deploy/docker/Dockerfile"
        text = dockerfile.read_text(encoding="utf-8", errors="ignore") if dockerfile.exists() else ""
        return {
            "name": "docker_hardening",
            "ok": "USER " in text or "useradd" in text,
            "message": "Dockerfile should run as non-root user.",
        }
