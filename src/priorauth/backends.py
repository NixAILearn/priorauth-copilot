"""Model clients behind one small interface (D-044).

Every client takes the same request (system blocks, one user message, a JSON schema) and
returns raw text plus usage. The extractor validates the text; no client interprets it.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from priorauth.config import ModelConfig

Role = Literal["extract", "hard"]
CHARS_PER_TOKEN = 3.0  # conservative for clinical text; over-estimates tokens on purpose


class ModelError(RuntimeError):
    """The call failed or returned nothing usable (refusal, truncation, HTTP error)."""


class ContextTooSmall(ModelError):
    pass


@dataclass(frozen=True)
class Reply:
    text: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cache_read_tokens: int | None = None
    latency_s: float = 0.0


class ModelClient(Protocol):
    backend: str

    def model_for(self, role: Role) -> str | None: ...

    def complete(self, *, system: Sequence[str], user: str, schema: dict, role: Role) -> Reply: ...


def estimate_tokens(*texts: str) -> int:
    return int(sum(len(t) for t in texts) / CHARS_PER_TOKEN) + 1


def check_fits(cfg: ModelConfig, system: Sequence[str], user: str) -> None:
    need = estimate_tokens(*system, user) + cfg.max_output_tokens
    if need > cfg.context_tokens:
        raise ContextTooSmall(
            f"prompt needs about {need} tokens with output, but {cfg.backend} is configured for "
            f"{cfg.context_tokens}; load the model with a longer context and set "
            "PRIORAUTH_CONTEXT_TOKENS"
        )


# --- Anthropic (official scorecard backend) ---------------------------------------------------


class AnthropicClient:
    """Claude via the official SDK: structured JSON output, cached system prompt.

    The system prompt and the policy block are identical for every case of a service, so the
    cache breakpoint sits on the last system block (kickoff section 9, cost control).
    Server-side refusal fallback is on; a refusal that survives it is a ModelError.
    """

    backend = "anthropic"

    def __init__(self, cfg: ModelConfig, sdk_client: Any | None = None):
        self.cfg = cfg
        if sdk_client is None:
            import anthropic  # imported here so other backends don't need the SDK configured

            sdk_client = anthropic.Anthropic(api_key=cfg.api_key) if cfg.api_key else None
            sdk_client = sdk_client or anthropic.Anthropic()
        self._sdk = sdk_client

    def model_for(self, role: Role) -> str | None:
        return self.cfg.extract_model if role == "extract" else self.cfg.hard_model

    def complete(self, *, system: Sequence[str], user: str, schema: dict, role: Role) -> Reply:
        model = self.model_for(role)
        if model is None:
            raise ModelError(f"no model configured for role {role}")
        blocks: list[dict[str, Any]] = [{"type": "text", "text": s} for s in system]
        blocks[-1]["cache_control"] = {"type": "ephemeral"}
        start = time.monotonic()
        with self._sdk.beta.messages.stream(
            model=model,
            max_tokens=self.cfg.max_output_tokens,
            system=blocks,
            messages=[{"role": "user", "content": user}],
            output_config={"format": {"type": "json_schema", "schema": schema}},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        ) as stream:
            msg = stream.get_final_message()
        latency = time.monotonic() - start
        if msg.stop_reason in ("refusal", "max_tokens"):
            raise ModelError(f"{model} stopped with {msg.stop_reason}")
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        u = msg.usage
        return Reply(
            text=text,
            model=getattr(msg, "model", model),
            input_tokens=getattr(u, "input_tokens", None),
            output_tokens=getattr(u, "output_tokens", None),
            cache_read_tokens=getattr(u, "cache_read_input_tokens", None),
            latency_s=latency,
        )


# --- OpenAI-compatible (OpenRouter, LM Studio) ------------------------------------------------


class OpenAICompatClient:
    """Chat Completions over HTTP with a JSON-schema response format.

    Used for OpenRouter (cheap dev runs) and LM Studio (local smoke tests). Neither counts
    toward the scorecard (D-044).
    """

    def __init__(self, cfg: ModelConfig, http_client: Any | None = None, timeout: float = 600):
        import httpx2

        if not cfg.base_url:
            raise ValueError(f"{cfg.backend}: no base URL")
        self.cfg = cfg
        self.backend = cfg.backend
        self._http = http_client or httpx2.Client(timeout=timeout)

    def model_for(self, role: Role) -> str | None:
        return self.cfg.extract_model if role == "extract" else self.cfg.hard_model

    def payload(self, *, system: Sequence[str], user: str, schema: dict, model: str) -> dict:
        return {
            "model": model,
            "max_tokens": self.cfg.max_output_tokens,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": "\n\n".join(system)},
                {"role": "user", "content": user},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "extraction", "strict": True, "schema": schema},
            },
        }

    def complete(self, *, system: Sequence[str], user: str, schema: dict, role: Role) -> Reply:
        model = self.model_for(role)
        if model is None:
            raise ModelError(f"no model configured for role {role}")
        check_fits(self.cfg, system, user)
        headers = {"Authorization": f"Bearer {self.cfg.api_key}"} if self.cfg.api_key else {}
        start = time.monotonic()
        try:
            r = self._http.post(
                f"{self.cfg.base_url.rstrip('/')}/chat/completions",  # type: ignore[union-attr]
                json=self.payload(system=system, user=user, schema=schema, model=model),
                headers=headers,
            )
        except Exception as e:  # connection refused (LM Studio not running), timeouts
            raise ModelError(f"{self.backend}: {type(e).__name__}: {e}") from e
        latency = time.monotonic() - start
        if r.status_code >= 400:
            raise ModelError(f"{self.backend} HTTP {r.status_code}: {r.text[:300]}")
        body = r.json()
        choice = (body.get("choices") or [{}])[0]
        if choice.get("finish_reason") == "length":
            raise ModelError(f"{model} hit the output limit")
        text = (choice.get("message") or {}).get("content") or ""
        usage = body.get("usage") or {}
        return Reply(
            text=text,
            model=body.get("model", model),
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            latency_s=latency,
        )


# --- Fake (tests and offline runs) ------------------------------------------------------------

Responder = Callable[[Sequence[str], str, Role], str]


@dataclass
class FakeClient:
    """Replays scripted replies in order: a str, an Exception to raise, or a callable."""

    replies: list[str | Exception | Responder]
    backend: str = "fake"
    hard_model: str | None = "fake-hard"
    calls: list[dict] = field(default_factory=list)

    def model_for(self, role: Role) -> str | None:
        return "fake-extract" if role == "extract" else self.hard_model

    def complete(self, *, system: Sequence[str], user: str, schema: dict, role: Role) -> Reply:
        self.calls.append({"system": list(system), "user": user, "role": role})
        if not self.replies:
            raise ModelError("fake client has no reply left")
        r = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        if isinstance(r, Exception):
            raise r
        text = r(system, user, role) if callable(r) else r
        return Reply(text=text, model=self.model_for(role) or "fake", input_tokens=0)


def make_client(cfg: ModelConfig) -> ModelClient:
    if cfg.backend == "anthropic":
        return AnthropicClient(cfg)
    if cfg.backend in ("openrouter", "lmstudio"):
        return OpenAICompatClient(cfg, timeout=cfg.timeout_s)
    raise ValueError("the fake backend is built in tests with FakeClient(replies)")
