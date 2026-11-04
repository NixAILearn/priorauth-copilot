"""Model backend configuration, read from environment variables (D-044).

Only the model calls change between backends. Quote checks, derived values, thresholds and
routing are code and run the same on every backend.

    PRIORAUTH_BACKEND          anthropic (default) | openrouter | lmstudio | fake
    PRIORAUTH_EXTRACT_MODEL    overrides the extraction model for the chosen backend
    PRIORAUTH_HARD_MODEL       overrides the hard-case model; "none" turns the re-run off
    PRIORAUTH_CONTEXT_TOKENS   context length the model was loaded with (lmstudio: 32k)
    PRIORAUTH_MAX_OUTPUT_TOKENS
    PRIORAUTH_BASE_URL         overrides the OpenAI-compatible endpoint
    PRIORAUTH_TIMEOUT_S        per-call HTTP timeout (default 600; lmstudio 3600, a local model
                               can take many minutes to write one case's JSON)
    ANTHROPIC_API_KEY          anthropic (the SDK also accepts an `ant auth login` profile)
    OPENROUTER_API_KEY         openrouter
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

Backend = Literal["anthropic", "openrouter", "lmstudio", "fake"]
BACKENDS: tuple[Backend, ...] = ("anthropic", "openrouter", "lmstudio", "fake")

MIN_LOCAL_CONTEXT = 32_768  # a full case packet plus the policy needs about 20-30k tokens

DEFAULTS: dict[Backend, dict[str, str | int | None]] = {
    # Official scorecard backend (kickoff section 9).
    "anthropic": {
        "extract": "claude-sonnet-5-5",
        "hard": "claude-opus-5-5",
        "base_url": None,
        "context": 1_000_000,
    },
    # No default model: OpenRouter's catalog changes often, so the run names one explicitly.
    "openrouter": {
        "extract": None,
        "hard": None,
        "base_url": "https://openrouter.ai/api/v1",
        "context": 128_000,
    },
    # LM Studio serves whatever model is loaded; this ID must match `lms ls` on Nick's Mac.
    "lmstudio": {
        "extract": "google/gemma-4-12b",
        "hard": None,
        "base_url": "http://localhost:1234/v1",
        "context": MIN_LOCAL_CONTEXT,
    },
    "fake": {"extract": "fake-extract", "hard": "fake-hard", "base_url": None, "context": 10**9},
}


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class ModelConfig:
    backend: Backend
    extract_model: str
    hard_model: str | None  # None: no hard-case re-run
    base_url: str | None
    api_key: str | None
    context_tokens: int
    max_output_tokens: int
    timeout_s: float = 600.0

    @property
    def official(self) -> bool:
        """Scorecard backends: local Gemma on LM Studio is the v0.1 headline (D-057); Anthropic
        stays a scorecard backend for when a key exists. OpenRouter and fake runs never count."""
        return self.backend in ("anthropic", "lmstudio")


def load_config(env: Mapping[str, str] | None = None) -> ModelConfig:
    env = os.environ if env is None else env
    backend = env.get("PRIORAUTH_BACKEND", "anthropic").strip().lower()
    if backend not in BACKENDS:
        raise ConfigError(f"PRIORAUTH_BACKEND={backend!r}; choose one of {', '.join(BACKENDS)}")
    d = DEFAULTS[backend]  # type: ignore[index]

    extract = env.get("PRIORAUTH_EXTRACT_MODEL") or d["extract"]
    if not extract:
        raise ConfigError(f"{backend}: set PRIORAUTH_EXTRACT_MODEL to a model ID")
    hard_env = env.get("PRIORAUTH_HARD_MODEL")
    hard = d["hard"] if hard_env is None else (None if hard_env.lower() == "none" else hard_env)

    api_key = {
        "anthropic": env.get("ANTHROPIC_API_KEY"),
        "openrouter": env.get("OPENROUTER_API_KEY"),
        "lmstudio": env.get("LMSTUDIO_API_KEY", "lm-studio"),  # LM Studio ignores the key
        "fake": None,
    }[backend]
    if backend == "openrouter" and not api_key:
        raise ConfigError("openrouter: set OPENROUTER_API_KEY")

    context = int(env.get("PRIORAUTH_CONTEXT_TOKENS") or d["context"])  # type: ignore[arg-type]
    if backend == "lmstudio" and context < MIN_LOCAL_CONTEXT:
        raise ConfigError(
            f"lmstudio: context {context} is below {MIN_LOCAL_CONTEXT}; load the model with "
            f"`lms load <model> --context-length {MIN_LOCAL_CONTEXT}` and set "
            "PRIORAUTH_CONTEXT_TOKENS to match"
        )
    return ModelConfig(
        backend=backend,  # type: ignore[arg-type]
        extract_model=str(extract),
        hard_model=str(hard) if hard else None,
        base_url=env.get("PRIORAUTH_BASE_URL") or d["base_url"],  # type: ignore[arg-type]
        api_key=api_key,
        context_tokens=context,
        # A full case is about 2-5k output tokens; a local model that loops should fail fast.
        max_output_tokens=int(
            env.get("PRIORAUTH_MAX_OUTPUT_TOKENS") or (8_000 if backend == "lmstudio" else 16_000)
        ),
        timeout_s=float(env.get("PRIORAUTH_TIMEOUT_S") or (3600 if backend == "lmstudio" else 600)),
    )
