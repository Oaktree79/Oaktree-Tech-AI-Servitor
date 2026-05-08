from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional
import hashlib
import json
import os


DEFAULT_IGNORE_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".venv", "venv", "node_modules", "dist", "build", ".next", ".turbo"
}

TEXT_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".txt", ".toml",
    ".yaml", ".yml", ".css", ".html", ".sql", ".sh", ".env.example"
}


@dataclass
class FileNode:
    path: str
    kind: str
    extension: str
    size_bytes: int
    depth: int
    sha256: Optional[str] = None
    line_count: Optional[int] = None
    language: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


class FileSystemMatrix:
    """
    Builds a searchable project file matrix.

    The matrix is intentionally simple:
    - one row per file/directory
    - metadata columns for path, kind, size, depth, hash, lines, language
    - JSON export for tooling and AI coding agents
    """

    def __init__(self, root: str | Path, ignore_dirs: Optional[Iterable[str]] = None):
        self.root = Path(root).resolve()
        self.ignore_dirs = set(ignore_dirs or DEFAULT_IGNORE_DIRS)
        self.nodes: List[FileNode] = []

    def _should_skip_dir(self, path: Path) -> bool:
        return path.name in self.ignore_dirs

    def _language_for(self, path: Path) -> Optional[str]:
        mapping = {
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "typescript-react",
            ".js": "javascript",
            ".jsx": "javascript-react",
            ".json": "json",
            ".md": "markdown",
            ".toml": "toml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".css": "css",
            ".html": "html",
            ".sql": "sql",
            ".sh": "shell",
        }
        return mapping.get(path.suffix.lower())

    def _hash_file(self, path: Path) -> str:
        digest = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _line_count(self, path: Path) -> Optional[int]:
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except UnicodeDecodeError:
            return None

    def scan(self) -> "FileSystemMatrix":
        self.nodes.clear()
        for current, dirs, files in os.walk(self.root):
            current_path = Path(current)
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            rel_current = current_path.relative_to(self.root)
            depth = 0 if str(rel_current) == "." else len(rel_current.parts)

            if str(rel_current) != ".":
                self.nodes.append(FileNode(
                    path=str(rel_current),
                    kind="directory",
                    extension="",
                    size_bytes=0,
                    depth=depth,
                ))

            for filename in files:
                path = current_path / filename
                rel = path.relative_to(self.root)
                try:
                    stat = path.stat()
                except OSError:
                    continue

                self.nodes.append(FileNode(
                    path=str(rel),
                    kind="file",
                    extension=path.suffix.lower(),
                    size_bytes=stat.st_size,
                    depth=len(rel.parts) - 1,
                    sha256=self._hash_file(path) if stat.st_size <= 5_000_000 else None,
                    line_count=self._line_count(path),
                    language=self._language_for(path),
                ))
        return self

    def by_language(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for node in self.nodes:
            if node.language:
                counts[node.language] = counts.get(node.language, 0) + 1
        return dict(sorted(counts.items()))

    def summary(self) -> Dict:
        files = [n for n in self.nodes if n.kind == "file"]
        dirs = [n for n in self.nodes if n.kind == "directory"]
        return {
            "root": str(self.root),
            "files": len(files),
            "directories": len(dirs),
            "total_size_bytes": sum(n.size_bytes for n in files),
            "languages": self.by_language(),
        }

    def to_json(self) -> str:
        return json.dumps({
            "summary": self.summary(),
            "nodes": [node.to_dict() for node in self.nodes],
        }, indent=2)
