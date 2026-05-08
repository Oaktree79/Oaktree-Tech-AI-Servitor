from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List
import json

from .llm_provider import LLMMessage, LLMProvider, DryRunLLMProvider
from .patch_engine import PatchEngine, ManagedEdit
from .structured_patch import StructuredPatchParser
from .test_runner import TestRunner
from .security import SecurityScanner
from .vector_memory import VectorMemory
from .policy_engine import PolicyEngine


@dataclass
class AgentLoopResult:
    status: str
    attempts: int
    transaction_id: str | None
    test_result: Dict | None
    security_findings: List[Dict]
    notes: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


class ClosedLoopCodingAgent:
    """
    Plan -> generate structured patch -> apply -> test -> repair loop.

    Safe default:
    - DryRun provider does not create edits
    - policy must allow paths and risk
    - tests and security scan run after every application
    """

    def __init__(self, root: str | Path, llm: LLMProvider | None = None, max_attempts: int = 3):
        self.root = Path(root).resolve()
        self.llm = llm or DryRunLLMProvider()
        self.max_attempts = max_attempts
        self.patch_engine = PatchEngine(self.root)
        self.patch_parser = StructuredPatchParser()
        self.tests = TestRunner(self.root)
        self.security = SecurityScanner(self.root)
        self.memory = VectorMemory(self.root)
        self.policy = PolicyEngine(self.root)

    def run(self, instruction: str, context: Dict | None = None, auto_apply: bool = False) -> Dict:
        context = context or {}
        notes: List[str] = []
        last_error = ""

        self.memory.build_from_files()
        memory_hits = self.memory.search(instruction)

        for attempt in range(1, self.max_attempts + 1):
            prompt = self._make_prompt(instruction, context, memory_hits, last_error)
            response = self.llm.complete([
                LLMMessage("system", "Return only a JSON structured patch object. Use full-file edits only."),
                LLMMessage("user", prompt),
            ])

            try:
                patch = self.patch_parser.parse(response.text)
            except Exception as exc:
                notes.append(f"attempt {attempt}: patch parse failed: {exc}")
                last_error = str(exc)
                continue

            if not patch.edits:
                return AgentLoopResult(
                    status="no_edits_proposed",
                    attempts=attempt,
                    transaction_id=None,
                    test_result=None,
                    security_findings=[],
                    notes=notes + ["Provider returned no edits."],
                ).to_dict()

            policy = self.policy.evaluate_edits(instruction, patch.edits, auto_apply=auto_apply)
            if not policy["allowed"]:
                return AgentLoopResult(
                    status="blocked_by_policy",
                    attempts=attempt,
                    transaction_id=None,
                    test_result=None,
                    security_findings=[],
                    notes=notes + policy["reasons"],
                ).to_dict()

            if not auto_apply:
                return {
                    "status": "approval_required",
                    "attempts": attempt,
                    "summary": patch.summary,
                    "diff": self.patch_engine.diff(self._hydrate_before(patch.edits)),
                    "notes": notes,
                }

            edits = self._hydrate_before(patch.edits)
            tx = self.patch_engine.apply(edits)
            sec = self.security.scan()
            security_findings = [f.to_dict() for f in sec.findings]
            test_result = self.tests.run(patch.test_command)

            if test_result["returncode"] == 0 and not any(f["severity"] in {"critical", "high"} for f in security_findings):
                return AgentLoopResult(
                    status="succeeded",
                    attempts=attempt,
                    transaction_id=tx.id,
                    test_result=test_result,
                    security_findings=security_findings,
                    notes=notes,
                ).to_dict()

            self.patch_engine.rollback(tx.id)
            last_error = json.dumps({"test_result": test_result, "security_findings": security_findings})[:4000]
            notes.append(f"attempt {attempt}: tests/security failed; rolled back transaction {tx.id}")

        return AgentLoopResult(
            status="failed",
            attempts=self.max_attempts,
            transaction_id=None,
            test_result=None,
            security_findings=[],
            notes=notes,
        ).to_dict()

    def _hydrate_before(self, edits: List[ManagedEdit]) -> List[ManagedEdit]:
        hydrated: List[ManagedEdit] = []
        for edit in edits:
            target = self.root / edit.path
            before = target.read_text(encoding="utf-8") if target.exists() else ""
            hydrated.append(ManagedEdit(path=edit.path, before=before, after=edit.after))
        return hydrated

    def _make_prompt(self, instruction: str, context: Dict, memory_hits: List[Dict], last_error: str) -> str:
        return json.dumps({
            "instruction": instruction,
            "context": context,
            "memory_hits": memory_hits,
            "last_error": last_error,
            "required_response_schema": {
                "summary": "string",
                "edits": [{"path": "relative path", "after": "complete new file content"}],
                "test_command": ["python", "-m", "pytest", "-q"],
            },
        }, indent=2)
