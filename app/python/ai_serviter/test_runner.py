from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .sandbox import ToolSandbox


class TestRunner:
    def __init__(self, root: str | Path, sandbox: ToolSandbox | None = None):
        self.root = Path(root).resolve()
        self.sandbox = sandbox or ToolSandbox(self.root, timeout_seconds=120)

    def detect_command(self) -> List[str]:
        if (self.root / "pyproject.toml").exists() or (self.root / "pytest.ini").exists() or (self.root / "tests").exists():
            return ["python", "-m", "pytest", "-q"]
        if (self.root / "package.json").exists():
            return ["npm", "test"]
        return ["python", "-m", "compileall", "-q", "."]

    def run(self, command: List[str] | None = None) -> Dict:
        result = self.sandbox.run(command or self.detect_command(), cwd=self.root)
        return result.to_dict()
