from __future__ import annotations

from pathlib import Path


class ProjectRootResolver:
    """
    Resolves the true repository root even when commands are run from python/.
    """

    MARKERS = [
        "deploy",
        "README.md",
        ".github",
        "python/pyproject.toml",
    ]

    def __init__(self, start: str | Path = "."):
        self.start = Path(start).resolve()

    def resolve(self) -> Path:
        candidates = [self.start, *self.start.parents]
        for candidate in candidates:
            if all((candidate / marker).exists() for marker in ["python"]) and (
                (candidate / "deploy").exists() or (candidate / ".github").exists()
            ):
                return candidate
            if (candidate / "pyproject.toml").exists() and candidate.name == "python":
                return candidate.parent
        return self.start
