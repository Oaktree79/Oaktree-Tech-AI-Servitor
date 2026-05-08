from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List
import difflib
import json
import time


@dataclass
class ManagedEdit:
    path: str
    before: str
    after: str


@dataclass
class PatchTransaction:
    id: str
    created_at: float
    edits: List[ManagedEdit]

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "edits": [asdict(e) for e in self.edits],
        }


class PatchEngine:
    """
    Applies managed full-file edits and supports rollback.

    This avoids fragile third-party patch parsing by tracking before/after contents
    for each file. You can still export a unified diff for review.
    """

    def __init__(self, root: str | Path, state_dir: str | Path = ".serviter/patches"):
        self.root = Path(root).resolve()
        self.state_dir = self.root / state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def create_edit(self, relative_path: str, after: str) -> ManagedEdit:
        path = self.root / relative_path
        before = path.read_text(encoding="utf-8") if path.exists() else ""
        return ManagedEdit(path=relative_path, before=before, after=after)

    def diff(self, edits: List[ManagedEdit]) -> str:
        chunks: List[str] = []
        for edit in edits:
            chunks.extend(difflib.unified_diff(
                edit.before.splitlines(keepends=True),
                edit.after.splitlines(keepends=True),
                fromfile=f"a/{edit.path}",
                tofile=f"b/{edit.path}",
            ))
        return "".join(chunks)

    def apply(self, edits: List[ManagedEdit]) -> PatchTransaction:
        transaction = PatchTransaction(
            id=str(int(time.time() * 1000)),
            created_at=time.time(),
            edits=edits,
        )
        self._save(transaction)

        for edit in edits:
            target = self.root / edit.path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(edit.after, encoding="utf-8")

        return transaction

    def rollback(self, transaction_id: str) -> PatchTransaction:
        transaction = self._load(transaction_id)
        for edit in transaction.edits:
            target = self.root / edit.path
            if edit.before == "":
                if target.exists():
                    target.unlink()
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(edit.before, encoding="utf-8")
        return transaction

    def list_transactions(self) -> List[str]:
        return sorted(p.stem for p in self.state_dir.glob("*.json"))

    def _save(self, transaction: PatchTransaction):
        path = self.state_dir / f"{transaction.id}.json"
        path.write_text(json.dumps(transaction.to_dict(), indent=2), encoding="utf-8")

    def _load(self, transaction_id: str) -> PatchTransaction:
        path = self.state_dir / f"{transaction_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        return PatchTransaction(
            id=data["id"],
            created_at=data["created_at"],
            edits=[ManagedEdit(**e) for e in data["edits"]],
        )
