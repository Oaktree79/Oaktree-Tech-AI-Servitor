from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List
import json
import os

from .llm_provider import (
    DryRunLLMProvider,
    LLMMessage,
    LLMProvider,
    OpenAICompatibleProvider,
    LocalCommandLLMProvider,
)


@dataclass
class LLMRuntimeStatus:
    provider: str
    model: str
    configured: bool
    notes: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


class LLMRuntime:
    """
    Production-facing LLM runtime selector.

    Supports:
    - dry-run
    - OpenAI-compatible HTTP API
    - local command model

    This module centralizes model selection, health checks, and safe prompt execution.
    """

    def __init__(self, config: Dict | None = None):
        self.config = config or {}
        self.provider = self._build_provider()

    def _build_provider(self) -> LLMProvider:
        cfg = self.config.get("llm", {})
        provider = cfg.get("provider") or os.getenv("SERVITER_LLM_PROVIDER", "dry-run")

        if provider == "openai-compatible":
            return OpenAICompatibleProvider(
                api_key=cfg.get("api_key") or os.getenv("OPENAI_API_KEY"),
                base_url=cfg.get("base_url") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                model=cfg.get("model") or os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            )

        if provider == "local-command":
            command = cfg.get("command") or os.getenv("SERVITER_LOCAL_LLM_COMMAND", "").split()
            if not command:
                raise ValueError("Local LLM command missing")
            return LocalCommandLLMProvider(command=command, model=cfg.get("model", "local-command"))

        return DryRunLLMProvider(cfg.get("model", "dry-run-coder"))

    def complete_json(self, instruction: str, schema: Dict, context: Dict | None = None) -> Dict:
        response = self.provider.complete([
            LLMMessage("system", "Return valid JSON only. Do not include markdown fences."),
            LLMMessage("user", json.dumps({
                "instruction": instruction,
                "schema": schema,
                "context": context or {},
            }, indent=2)),
        ])
        try:
            return json.loads(response.text)
        except Exception:
            return {
                "raw_text": response.text,
                "provider": response.provider,
                "model": response.model,
                "parse_error": True,
            }

    def status(self) -> Dict:
        name = self.provider.__class__.__name__
        model = getattr(self.provider, "model", "unknown")
        notes = []
        configured = True
        if isinstance(self.provider, DryRunLLMProvider):
            configured = False
            notes.append("Dry-run provider active. No external LLM calls will be made.")
        return LLMRuntimeStatus(name, model, configured, notes).to_dict()
