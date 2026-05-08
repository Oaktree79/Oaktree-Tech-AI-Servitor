from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple
import json
import math
import re
from collections import Counter


@dataclass
class MemoryDocument:
    id: str
    path: str
    text: str
    metadata: Dict

    def to_dict(self) -> Dict:
        return asdict(self)


class VectorMemory:
    """
    Dependency-free repository memory using lexical vectors.
    CamelCase and snake_case are split so queries like "plugin module"
    can match symbols like PluginModule.
    """

    def __init__(self, root: str | Path, state_path: str | Path = ".serviter/vector_memory.json"):
        self.root = Path(root).resolve()
        self.state_path = self.root / state_path
        self.documents: List[MemoryDocument] = []

    def _normalize(self, text: str) -> str:
        text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
        text = text.replace("_", " ")
        return text.lower()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-z][a-z0-9]{1,}", self._normalize(text))

    def _vector(self, text: str) -> Counter:
        return Counter(self._tokenize(text))

    def _cosine(self, a: Counter, b: Counter) -> float:
        if not a or not b:
            return 0.0
        dot = sum(a[k] * b.get(k, 0) for k in a)
        norm_a = math.sqrt(sum(v * v for v in a.values()))
        norm_b = math.sqrt(sum(v * v for v in b.values()))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

    def build_from_files(self, extensions: set[str] | None = None) -> "VectorMemory":
        extensions = extensions or {".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".json", ".toml", ".yaml", ".yml"}
        self.documents.clear()

        for path in self.root.rglob("*"):
            if path.is_dir():
                continue
            if any(part in {".git", ".venv", "venv", "node_modules", "__pycache__", ".serviter"} for part in path.parts):
                continue
            if path.suffix.lower() not in extensions:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            rel = str(path.relative_to(self.root))
            self.documents.append(MemoryDocument(
                id=rel,
                path=rel,
                text=text[:20000],
                metadata={"extension": path.suffix.lower(), "size": path.stat().st_size},
            ))

        return self

    def search(self, query: str, limit: int = 8) -> List[Dict]:
        qv = self._vector(query)
        scored: List[Tuple[float, MemoryDocument]] = []
        for doc in self.documents:
            score = self._cosine(qv, self._vector(doc.text + " " + doc.path))
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "score": round(score, 4),
                "path": doc.path,
                "snippet": doc.text[:800],
                "metadata": doc.metadata,
            }
            for score, doc in scored[:limit]
        ]

    def save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps({"documents": [d.to_dict() for d in self.documents]}, indent=2),
            encoding="utf-8",
        )

    def load(self) -> "VectorMemory":
        if not self.state_path.exists():
            return self
        data = json.loads(self.state_path.read_text(encoding="utf-8"))
        self.documents = [MemoryDocument(**d) for d in data.get("documents", [])]
        return self
