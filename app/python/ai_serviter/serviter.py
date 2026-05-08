from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import json

from .code_index import CodeIndex
from .filesystem_matrix import FileSystemMatrix
from .llm_provider import LLMMessage, LLMProvider, provider_from_config
from .patch_engine import ManagedEdit, PatchEngine
from .planner import CodingTaskPlanner
from .security import SecurityScanner
from .vector_memory import VectorMemory


class AIServiter:
    """
    AI Serviter Algorithm Coding Module.

    Coordinates:
    - file system matrix generation
    - code symbol indexing
    - deterministic task planning
    - LLM provider integration
    - managed patch apply/rollback
    - repository memory/vector retrieval
    - stronger security scanning
    """

    def __init__(self, root: str | Path, config: Dict | None = None, llm: LLMProvider | None = None):
        self.root = Path(root).resolve()
        self.config = config or {}
        self.matrix = FileSystemMatrix(self.root)
        self.index = CodeIndex(self.root)
        self.security = SecurityScanner(self.root)
        self.memory = VectorMemory(self.root)
        self.patches = PatchEngine(self.root)
        self.planner = CodingTaskPlanner()
        self.llm = llm or provider_from_config(self.config)

    def analyze(self) -> Dict:
        self.matrix.scan()
        self.index.build()
        self.security.scan()
        self.memory.build_from_files()
        return {
            "matrix": self.matrix.summary(),
            "symbol_count": len(self.index.symbols),
            "memory_documents": len(self.memory.documents),
            "security_findings": len(self.security.findings),
        }

    def plan(self, request: str) -> Dict:
        self.analyze()
        hits = [s.to_dict() for s in self.index.search(request)]
        memory_hits = self.memory.search(request)
        task = self.planner.plan(request, self.matrix.summary(), hits)
        return {
            "request": request,
            "analysis": {
                "matrix": self.matrix.summary(),
                "symbol_hits": hits[:25],
                "memory_hits": memory_hits[:8],
                "security_findings": [f.to_dict() for f in self.security.findings[:25]],
            },
            "task": task.to_dict(),
        }

    def propose(self, request: str) -> Dict:
        plan = self.plan(request)
        messages = [
            LLMMessage(role="system", content="You are AI Serviter, a careful coding assistant. Return concise implementation guidance and patch strategy."),
            LLMMessage(role="user", content=json.dumps(plan, indent=2)),
        ]
        response = self.llm.complete(messages)
        return {
            "request": request,
            "plan": plan,
            "proposal": {
                "provider": response.provider,
                "model": response.model,
                "text": response.text,
            },
        }

    def export_development_matrix(self, output_dir: str | Path) -> Dict[str, str]:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        self.matrix.scan()
        self.index.build()
        self.security.scan()
        self.memory.build_from_files()
        self.memory.save()

        files = {
            "filesystem_matrix.json": self.matrix.to_json(),
            "code_index.json": self.index.to_json(),
            "security_scan.json": self.security.to_json(),
            "memory_search_demo.json": json.dumps({"query": "plugin module", "results": self.memory.search("plugin module")}, indent=2),
        }

        written: Dict[str, str] = {}
        for filename, content in files.items():
            path = output / filename
            path.write_text(content, encoding="utf-8")
            written[filename] = str(path)

        return written

    def create_managed_edit(self, relative_path: str, after: str) -> ManagedEdit:
        return self.patches.create_edit(relative_path, after)

    def apply_edits(self, edits: List[ManagedEdit]) -> Dict:
        diff = self.patches.diff(edits)
        transaction = self.patches.apply(edits)
        return {
            "transaction": transaction.to_dict(),
            "diff": diff,
        }

    def rollback(self, transaction_id: str) -> Dict:
        transaction = self.patches.rollback(transaction_id)
        return transaction.to_dict()
