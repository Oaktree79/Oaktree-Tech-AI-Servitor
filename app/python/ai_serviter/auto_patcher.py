from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .llm_provider import LLMMessage, LLMProvider, DryRunLLMProvider
from .patch_engine import ManagedEdit, PatchEngine
from .test_runner import TestRunner
from .security import SecurityScanner


class AutoPatcher:
    """
    Automated patching scaffold.

    Safe mode behavior:
    - asks the LLM provider for a proposal
    - does not blindly parse arbitrary model output into file edits
    - supports explicit managed edits
    """

    def __init__(self, root: str | Path, llm: LLMProvider | None = None):
        self.root = Path(root).resolve()
        self.llm = llm or DryRunLLMProvider()
        self.engine = PatchEngine(self.root)
        self.tests = TestRunner(self.root)
        self.security = SecurityScanner(self.root)

    def propose_patch(self, instruction: str, context: Dict) -> Dict:
        response = self.llm.complete([
            LLMMessage("system", "You are a coding patch planner. Propose files to edit and test strategy. Do not invent secret values."),
            LLMMessage("user", f"Instruction: {instruction}\nContext:\n{context}"),
        ])
        return {
            "provider": response.provider,
            "model": response.model,
            "text": response.text,
        }

    def apply_managed_edits(self, edits: List[ManagedEdit], run_tests: bool = True) -> Dict:
        tx = self.engine.apply(edits)
        security = self.security.scan()
        test_result = self.tests.run() if run_tests else None
        return {
            "transaction": tx.to_dict(),
            "security_findings": [f.to_dict() for f in security.findings],
            "test_result": test_result,
        }
