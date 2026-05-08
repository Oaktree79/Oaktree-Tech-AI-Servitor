from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List
import os
import subprocess


@dataclass
class PRResult:
    provider: str
    command: List[str]
    returncode: int
    stdout: str
    stderr: str
    instructions: str

    def to_dict(self) -> Dict:
        return asdict(self)


class PullRequestAutomation:
    """
    GitHub/GitLab PR/MR automation scaffold.

    GitHub requires gh CLI.
    GitLab requires glab CLI.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def create_github_pr(self, title: str, body: str = "", base: str | None = None) -> Dict:
        cmd = ["gh", "pr", "create", "--title", title, "--body", body]
        if base:
            cmd += ["--base", base]
        return self._run("github", cmd, "Install GitHub CLI and run `gh auth login`.").to_dict()

    def create_gitlab_mr(self, title: str, description: str = "", target_branch: str | None = None) -> Dict:
        cmd = ["glab", "mr", "create", "--title", title, "--description", description]
        if target_branch:
            cmd += ["--target-branch", target_branch]
        return self._run("gitlab", cmd, "Install GitLab CLI and run `glab auth login`.").to_dict()

    def _run(self, provider: str, cmd: List[str], instructions: str) -> PRResult:
        exe = cmd[0]
        from shutil import which
        if which(exe) is None:
            return PRResult(provider, cmd, 127, "", f"{exe} not installed", instructions)
        proc = subprocess.run(cmd, cwd=self.root, capture_output=True, text=True, check=False)
        return PRResult(provider, cmd, proc.returncode, proc.stdout[-5000:], proc.stderr[-5000:], instructions)
