from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Protocol
import os
import json
import urllib.request


@dataclass
class LLMMessage:
    role: str
    content: str


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str


class LLMProvider(Protocol):
    def complete(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        ...


class DryRunLLMProvider:
    """
    Safe default provider. It does not call external APIs.
    It returns a deterministic response suitable for tests and local development.
    """

    def __init__(self, model: str = "dry-run-coder"):
        self.model = model

    def complete(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        prompt = "\n".join(f"{m.role}: {m.content}" for m in messages)
        return LLMResponse(
            text=(
                "DRY RUN RESPONSE\\n"
                "No external model was called. Review the plan, then connect OpenAICompatibleProvider "
                "or LocalCommandLLMProvider for generated code.\\n\\n"
                f"Prompt excerpt:\\n{prompt[:1000]}"
            ),
            provider="dry-run",
            model=self.model,
        )


class OpenAICompatibleProvider:
    """
    Minimal OpenAI-compatible chat-completions adapter using only stdlib urllib.

    Configure:
      export OPENAI_API_KEY=...
      export OPENAI_BASE_URL=https://api.openai.com/v1
      export OPENAI_MODEL=gpt-4.1-mini

    This avoids a hard dependency on the openai Python package.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAICompatibleProvider")

    def complete(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        body = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": kwargs.get("temperature", 0.2),
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=kwargs.get("timeout", 60)) as resp:
            parsed = json.loads(resp.read().decode("utf-8"))
        text = parsed["choices"][0]["message"]["content"]
        return LLMResponse(text=text, provider="openai-compatible", model=self.model)


class LocalCommandLLMProvider:
    """
    Adapter for local model CLIs.

    Example command:
      python -m ai_serviter.local_echo_model

    The full prompt is passed to stdin, and stdout becomes the completion.
    """

    def __init__(self, command: List[str], model: str = "local-command"):
        self.command = command
        self.model = model

    def complete(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        import subprocess
        prompt = "\n".join(f"{m.role}: {m.content}" for m in messages)
        proc = subprocess.run(
            self.command,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=kwargs.get("timeout", 120),
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr or f"Local command failed with code {proc.returncode}")
        return LLMResponse(text=proc.stdout, provider="local-command", model=self.model)


def provider_from_config(config: Dict) -> LLMProvider:
    llm_cfg = config.get("llm", {}) if isinstance(config, dict) else {}
    provider = llm_cfg.get("provider", "dry-run")

    if provider == "openai-compatible":
        return OpenAICompatibleProvider(
            api_key=llm_cfg.get("api_key"),
            base_url=llm_cfg.get("base_url"),
            model=llm_cfg.get("model"),
        )
    if provider == "local-command":
        command = llm_cfg.get("command")
        if not command:
            raise ValueError("llm.command is required for local-command provider")
        return LocalCommandLLMProvider(command=command, model=llm_cfg.get("model", "local-command"))
    return DryRunLLMProvider(model=llm_cfg.get("model", "dry-run-coder"))
