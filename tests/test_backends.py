"""Backend switching (D-044): config from env, payloads, and the local context guard."""

import json
from types import SimpleNamespace

import httpx2
import pytest

from priorauth.backends import (
    AnthropicClient,
    ContextTooSmall,
    ModelError,
    OpenAICompatClient,
    make_client,
)
from priorauth.config import ConfigError, load_config
from priorauth.extractor import OUTPUT_SCHEMA


def test_default_is_anthropic_with_the_kickoff_models():
    cfg = load_config({})
    assert (cfg.backend, cfg.extract_model, cfg.hard_model) == (
        "anthropic",
        "claude-sonnet-5-5",
        "claude-opus-5-5",
    )
    assert cfg.official


def test_openrouter_needs_a_key_and_a_model():
    with pytest.raises(ConfigError, match="OPENROUTER_API_KEY"):
        load_config({"PRIORAUTH_BACKEND": "openrouter", "PRIORAUTH_EXTRACT_MODEL": "x/y"})
    with pytest.raises(ConfigError, match="PRIORAUTH_EXTRACT_MODEL"):
        load_config({"PRIORAUTH_BACKEND": "openrouter", "OPENROUTER_API_KEY": "k"})
    cfg = load_config(
        {
            "PRIORAUTH_BACKEND": "openrouter",
            "OPENROUTER_API_KEY": "k",
            "PRIORAUTH_EXTRACT_MODEL": "x/y",
        }
    )
    assert cfg.base_url == "https://openrouter.ai/api/v1" and not cfg.official


def test_lmstudio_defaults_and_minimum_context():
    cfg = load_config({"PRIORAUTH_BACKEND": "lmstudio"})
    assert cfg.base_url == "http://localhost:1234/v1"
    assert cfg.context_tokens == 32_768 and cfg.hard_model is None
    with pytest.raises(ConfigError, match="below"):
        load_config({"PRIORAUTH_BACKEND": "lmstudio", "PRIORAUTH_CONTEXT_TOKENS": "8192"})


def test_unknown_backend_is_rejected():
    with pytest.raises(ConfigError):
        load_config({"PRIORAUTH_BACKEND": "gpt"})


def _compat(handler, **env):
    cfg = load_config({"PRIORAUTH_BACKEND": "lmstudio", **env})
    return OpenAICompatClient(
        cfg, http_client=httpx2.Client(transport=httpx2.MockTransport(handler))
    )


def test_openai_compatible_request_and_reply():
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content)
        return httpx2.Response(
            200,
            json={
                "model": "google/gemma-4-12b",
                "choices": [{"message": {"content": '{"ok": true}'}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 3},
            },
        )

    reply = _compat(handler).complete(
        system=["a", "b"], user="u", schema=OUTPUT_SCHEMA, role="extract"
    )
    assert seen["url"] == "http://localhost:1234/v1/chat/completions"
    assert seen["body"]["response_format"]["json_schema"]["schema"] == OUTPUT_SCHEMA
    assert seen["body"]["messages"][0] == {"role": "system", "content": "a\n\nb"}
    assert reply.text == '{"ok": true}' and reply.input_tokens == 10


def test_openai_compatible_errors_are_model_errors():
    client = _compat(lambda r: httpx2.Response(500, text="down"))
    with pytest.raises(ModelError, match="500"):
        client.complete(system=["s"], user="u", schema={}, role="extract")
    trunc = _compat(
        lambda r: httpx2.Response(
            200, json={"choices": [{"message": {"content": "{"}, "finish_reason": "length"}]}
        )
    )
    with pytest.raises(ModelError, match="output limit"):
        trunc.complete(system=["s"], user="u", schema={}, role="extract")


def test_local_prompt_that_cannot_fit_is_refused_before_sending():
    client = _compat(lambda r: pytest.fail("should not send"))
    with pytest.raises(ContextTooSmall):
        client.complete(system=["x" * 200_000], user="u", schema={}, role="extract")


class _Stream:
    def __init__(self, msg, kwargs, log):
        self.msg, log["kwargs"] = msg, kwargs

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get_final_message(self):
        return self.msg


def _sdk(msg, log):
    beta = SimpleNamespace(messages=SimpleNamespace(stream=lambda **kw: _Stream(msg, kw, log)))
    return SimpleNamespace(beta=beta)


def test_anthropic_request_shape_and_usage():
    log = {}
    msg = SimpleNamespace(
        stop_reason="end_turn",
        model="claude-sonnet-5-5",
        content=[SimpleNamespace(type="text", text='{"values": []}')],
        usage=SimpleNamespace(input_tokens=100, output_tokens=20, cache_read_input_tokens=80),
    )
    client = AnthropicClient(load_config({}), sdk_client=_sdk(msg, log))
    reply = client.complete(
        system=["sys", "policy"], user="docs", schema=OUTPUT_SCHEMA, role="extract"
    )
    kw = log["kwargs"]
    assert kw["model"] == "claude-sonnet-5-5"
    assert kw["system"][-1]["cache_control"] == {"type": "ephemeral"}
    assert "cache_control" not in kw["system"][0]
    assert kw["output_config"]["format"] == {"type": "json_schema", "schema": OUTPUT_SCHEMA}
    assert "tool_choice" not in kw  # forced tool use is not accepted by these models
    assert reply.cache_read_tokens == 80
    client.complete(system=["s"], user="u", schema={}, role="hard")
    assert log["kwargs"]["model"] == "claude-opus-5-5"


def test_anthropic_refusal_is_a_model_error():
    msg = SimpleNamespace(stop_reason="refusal", content=[], usage=None)
    client = AnthropicClient(load_config({}), sdk_client=_sdk(msg, {}))
    with pytest.raises(ModelError, match="refusal"):
        client.complete(system=["s"], user="u", schema={}, role="extract")


def test_make_client_picks_the_backend():
    assert isinstance(
        make_client(load_config({"PRIORAUTH_BACKEND": "lmstudio"})), OpenAICompatClient
    )
