from __future__ import annotations

from pathlib import Path
from typing import Dict
import json
import secrets


class ConfigWizard:
    """
    Non-interactive and interactive configuration wizard backend.
    GUI/installer can call this module.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.config_path = self.root / ".serviter" / "config.json"

    def defaults(self) -> Dict:
        return {
            "host": "127.0.0.1",
            "port": 8765,
            "llm_provider": "dry-run",
            "auto_start_worker": True,
            "open_dashboard_on_start": True,
            "require_approval_for_risky_tasks": True,
        }

    def create(self, overrides: Dict | None = None) -> Dict:
        data = self.defaults()
        if overrides:
            data.update(overrides)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data

    def load(self) -> Dict:
        if not self.config_path.exists():
            return self.create()
        return json.loads(self.config_path.read_text(encoding="utf-8"))

    def generate_secrets(self) -> Dict:
        env_path = self.root / ".serviter" / ".env"
        env_path.parent.mkdir(parents=True, exist_ok=True)
        admin_password = secrets.token_urlsafe(18)
        token_secret = secrets.token_urlsafe(48)
        env_path.write_text(
            f"SERVITER_ADMIN_PASSWORD={admin_password}\nSERVITER_SECRET={token_secret}\n",
            encoding="utf-8",
        )
        return {"env_file": str(env_path), "admin_password": admin_password}
