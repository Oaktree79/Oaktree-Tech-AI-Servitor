from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import shutil

from .container_sandbox import DockerSandbox
from .sandbox import ToolSandbox


class IsolationManager:
    """
    Selects the strongest available sandbox.

    Priority:
    1. Docker sandbox if docker exists
    2. local command sandbox fallback
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.docker = DockerSandbox(self.root)
        self.local = ToolSandbox(self.root)

    def status(self) -> Dict:
        return {
            "docker_available": self.docker.available(),
            "local_sandbox_available": True,
            "recommended": "docker" if self.docker.available() else "local",
            "warning": None if self.docker.available() else "Local sandbox is not a hardened isolation boundary.",
        }

    def run(self, command: List[str], prefer: str = "docker") -> Dict:
        if prefer == "docker" and self.docker.available():
            return self.docker.run(command).to_dict()
        return self.local.run(command).to_dict()
