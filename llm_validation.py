from __future__ import annotations

from typing import Dict
import json

from .llm_runtime import LLMRuntime
from .structured_patch import StructuredPatchParser


class LLMConfigValidator:
    def __init__(self, runtime: LLMRuntime | None = None):
        self.runtime = runtime or LLMRuntime()

    def validate_status(self) -> Dict:
        status = self.runtime.status()
        return {
            "ok": bool(status.get("provider")),
            "status": status,
            "ready_for_real_edits": status.get("configured", False),
        }

    def validate_structured_patch_contract(self) -> Dict:
        schema = {
            "summary": "string",
            "edits": [{"path": "relative path", "after": "complete file content"}],
            "test_command": ["python", "-m", "pytest", "-q"],
        }
        result = self.runtime.complete_json(
            "Return an empty patch for validation only.",
            schema=schema,
            context={"must_return_json": True},
        )

        if result.get("parse_error"):
            return {"ok": False, "result": result, "reason": "provider did not return parseable JSON"}

        try:
            text = json.dumps(result)
            StructuredPatchParser().parse(text)
            return {"ok": True, "result": result}
        except Exception as exc:
            return {"ok": False, "result": result, "reason": str(exc)}
