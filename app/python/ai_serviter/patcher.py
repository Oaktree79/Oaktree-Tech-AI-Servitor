from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List
import difflib


@dataclass
class FileEdit:
    path: str
    before: str
    after: str


class UnifiedPatchBuilder:
    def build(self, edits: List[FileEdit]) -> str:
        chunks: List[str] = []
        for edit in edits:
            before_lines = edit.before.splitlines(keepends=True)
            after_lines = edit.after.splitlines(keepends=True)
            chunks.extend(difflib.unified_diff(
                before_lines,
                after_lines,
                fromfile=f"a/{edit.path}",
                tofile=f"b/{edit.path}",
            ))
        return "".join(chunks)

    def replace_text(self, root: str | Path, relative_path: str, old: str, new: str) -> FileEdit:
        path = Path(root) / relative_path
        before = path.read_text(encoding="utf-8")
        if old not in before:
            raise ValueError(f"Text not found in {relative_path}")
        after = before.replace(old, new, 1)
        return FileEdit(relative_path, before, after)
