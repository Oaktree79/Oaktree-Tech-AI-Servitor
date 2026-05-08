from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional
import ast
import json


@dataclass
class SymbolRecord:
    name: str
    kind: str
    path: str
    line: int
    end_line: Optional[int]
    signature: Optional[str] = None
    docstring: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


class CodeIndex:
    """
    Lightweight static code index.

    Python support uses the built-in AST.
    TypeScript/JS support uses regex-level export discovery to stay dependency-free.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.symbols: List[SymbolRecord] = []

    def build(self) -> "CodeIndex":
        self.symbols.clear()
        for path in self.root.rglob("*"):
            if path.is_dir():
                continue
            if any(part in {".git", ".venv", "venv", "node_modules", "__pycache__"} for part in path.parts):
                continue
            if path.suffix == ".py":
                self._index_python(path)
            elif path.suffix in {".ts", ".tsx", ".js", ".jsx"}:
                self._index_ts_js(path)
        return self

    def _index_python(self, path: Path):
        rel = str(path.relative_to(self.root))
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            return

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args]
                signature = f"{node.name}({', '.join(args)})"
                self.symbols.append(SymbolRecord(
                    name=node.name,
                    kind="async_function" if isinstance(node, ast.AsyncFunctionDef) else "function",
                    path=rel,
                    line=node.lineno,
                    end_line=getattr(node, "end_lineno", None),
                    signature=signature,
                    docstring=ast.get_docstring(node),
                ))
            elif isinstance(node, ast.ClassDef):
                self.symbols.append(SymbolRecord(
                    name=node.name,
                    kind="class",
                    path=rel,
                    line=node.lineno,
                    end_line=getattr(node, "end_lineno", None),
                    signature=f"class {node.name}",
                    docstring=ast.get_docstring(node),
                ))

    def _index_ts_js(self, path: Path):
        rel = str(path.relative_to(self.root))
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception:
            return

        patterns = [
            ("function", "function "),
            ("class", "class "),
            ("export", "export "),
        ]

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            for kind, marker in patterns:
                if marker in stripped:
                    name = self._extract_name(stripped, marker)
                    if name:
                        self.symbols.append(SymbolRecord(
                            name=name,
                            kind=kind,
                            path=rel,
                            line=idx,
                            end_line=None,
                            signature=stripped[:180],
                            docstring=None,
                        ))
                    break

    def _extract_name(self, line: str, marker: str) -> Optional[str]:
        try:
            after = line.split(marker, 1)[1].strip()
        except IndexError:
            return None
        token = after.split("(", 1)[0].split("{", 1)[0].split("=", 1)[0].strip()
        token = token.replace("default", "").replace("async", "").strip()
        token = token.split()[-1] if token.split() else token
        return token or None

    def search(self, query: str) -> List[SymbolRecord]:
        q = query.lower()
        return [
            s for s in self.symbols
            if q in s.name.lower()
            or q in s.path.lower()
            or (s.signature and q in s.signature.lower())
            or (s.docstring and q in s.docstring.lower())
        ]

    def to_json(self) -> str:
        return json.dumps({"symbols": [s.to_dict() for s in self.symbols]}, indent=2)
