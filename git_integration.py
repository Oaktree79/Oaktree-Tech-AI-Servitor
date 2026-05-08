from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List
import subprocess
import time


@dataclass
class GitResult:
    command: List[str]
    returncode: int
    stdout: str
    stderr: str

    def to_dict(self) -> Dict:
        return asdict(self)


class GitIntegration:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def run(self, args: List[str]) -> GitResult:
        proc = subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, check=False)
        return GitResult(["git", *args], proc.returncode, proc.stdout[-5000:], proc.stderr[-5000:])

    def available(self) -> bool:
        return (self.root / ".git").exists()

    def create_branch(self, prefix: str = "ai-serviter") -> Dict:
        name = f"{prefix}-{int(time.time())}"
        return self.run(["checkout", "-b", name]).to_dict()

    def status(self) -> Dict:
        return self.run(["status", "--short"]).to_dict()

    def diff(self) -> Dict:
        return self.run(["diff"]).to_dict()

    def commit_all(self, message: str) -> Dict:
        add = self.run(["add", "."]).to_dict()
        commit = self.run(["commit", "-m", message]).to_dict()
        return {"add": add, "commit": commit}

    def pr_instructions(self, title: str, body: str = "") -> Dict:
        return {
            "github_cli": ["gh", "pr", "create", "--title", title, "--body", body],
            "note": "Install GitHub CLI and authenticate with `gh auth login` to create PRs automatically.",
        }
