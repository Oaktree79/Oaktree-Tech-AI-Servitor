from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import json
import re

from .patch_engine import ManagedEdit


@dataclass
class StructuredPatch:
    summary: str
    edits: List[ManagedEdit]
    test_command: List[str] | None = None


class StructuredPatchParser:
    """
    Parses safe JSON patch responses from an LLM.

    Required format:
    {
      "summary": "...",
      "edits": [
        {"path": "relative/file.py", "after": "full file content"}
      ],
      "test_command": ["python", "-m", "pytest", "-q"]
    }

    It intentionally does not support arbitrary shell commands.
    """

    def extract_json(self, text: str) -> Dict:
        text = text.strip()
        if text.startswith("{"):
            return json.loads(text)

        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S)
        if fenced:
            return json.loads(fenced.group(1))

        raise ValueError("No JSON patch object found in model response")

    def parse(self, text: str) -> StructuredPatch:
        data = self.extract_json(text)
        edits: List[ManagedEdit] = []
        for edit in data.get("edits", []):
            path = edit["path"]
            before = edit.get("before", "")
            after = edit["after"]
            if path.startswith("/") or ".." in path.split("/"):
                raise ValueError(f"Unsafe path in patch: {path}")
            edits.append(ManagedEdit(path=path, before=before, after=after))
        test_command = data.get("test_command")
        if test_command is not None and not isinstance(test_command, list):
            raise ValueError("test_command must be a list")
        return StructuredPatch(
            summary=data.get("summary", ""),
            edits=edits,
            test_command=test_command,
        )
