from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import os
import secrets
import subprocess
import sys
import venv


class EnvironmentSetup:
    """
    Creates local venv, installs dependencies, generates .env, and prepares folders.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.python_dir = self.root / "python"
        self.venv_dir = self.root / ".venv"
        self.env_file = self.root / ".serviter" / ".env"

    def create_venv(self) -> Dict:
        if not self.venv_dir.exists():
            venv.EnvBuilder(with_pip=True).create(self.venv_dir)
        return {"ok": self.venv_dir.exists(), "venv": str(self.venv_dir)}

    def python_executable(self) -> Path:
        if os.name == "nt":
            return self.venv_dir / "Scripts" / "python.exe"
        return self.venv_dir / "bin" / "python"

    def install_dependencies(self, extras: str = "dev") -> Dict:
        self.create_venv()
        py = self.python_executable()
        cmd = [str(py), "-m", "pip", "install", "-e", f"{self.python_dir}[{extras}]"]
        proc = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, check=False)
        return {"ok": proc.returncode == 0, "command": cmd, "stdout": proc.stdout[-5000:], "stderr": proc.stderr[-5000:]}

    def generate_env(self, admin_password: str | None = None, overwrite: bool = False) -> Dict:
        self.env_file.parent.mkdir(parents=True, exist_ok=True)
        if self.env_file.exists() and not overwrite:
            return {"ok": True, "env_file": str(self.env_file), "created": False}

        admin_password = admin_password or secrets.token_urlsafe(18)
        secret = secrets.token_urlsafe(48)
        content = (
            f"SERVITER_ADMIN_PASSWORD={admin_password}\n"
            f"SERVITER_SECRET={secret}\n"
            "SERVITER_TLS_TERMINATED=0\n"
            "SERVITER_LLM_PROVIDER=dry-run\n"
        )
        self.env_file.write_text(content, encoding="utf-8")
        return {"ok": True, "env_file": str(self.env_file), "created": True, "admin_password": admin_password}

    def prepare(self) -> Dict:
        (self.root / ".serviter").mkdir(parents=True, exist_ok=True)
        (self.root / "logs").mkdir(parents=True, exist_ok=True)
        (self.root / "backups").mkdir(parents=True, exist_ok=True)
        env = self.generate_env()
        venv_result = self.create_venv()
        deps = self.install_dependencies()
        return {"env": env, "venv": venv_result, "dependencies": deps}
