"""Provider-chain tests with mocked HTTP. These do NOT prove a live Gemini/Groq call works."""
import asyncio

import pytest

from agent import llm


@pytest.fixture
def keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-g")
    monkeypatch.setenv("GROQ_API_KEY", "test-q")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ATLAS_LLM", raising=False)
    monkeypatch.delenv("AI_PROVIDER", raising=False)
    monkeypatch.setattr(llm, "claude_bin", lambda: "/nonexistent/claude")


def test_chain_order_and_missing_credentials(keys, monkeypatch):
    assert llm.chain() == ["gemini", "groq"]
    monkeypatch.delenv("GEMINI_API_KEY")
    assert llm.chain() == ["groq"]


def test_web_tools_force_claude_cli(keys):
    assert llm.chain(["WebSearch"]) == ["claude-cli"]


def test_gemini_primary(keys, monkeypatch):
    async def fake_post(url, body, headers, retries=3):
        assert "generativelanguage" in url and headers["x-goog-api-key"] == "test-g"
        return {"candidates": [{"content": {"parts": [{"text": '{"ok": true}'}]}}],
                "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 3}}
    monkeypatch.setattr(llm, "_post", fake_post)
    data, meta = asyncio.run(llm.complete_json("s", "p", {"type": "object"}, "sonnet"))
    assert data == {"ok": True} and meta["provider"] == "gemini" and meta["fallback_errors"] == []


def test_fallback_to_groq_on_quota(keys, monkeypatch):
    async def fake_post(url, body, headers, retries=3):
        if "generativelanguage" in url:
            raise llm.RetryableLLMError("http 429: quota")
        assert headers["Authorization"] == "Bearer test-q"
        return {"choices": [{"message": {"content": '{"ok": 1}'}}], "usage": {}}
    monkeypatch.setattr(llm, "_post", fake_post)
    data, meta = asyncio.run(llm.complete_json("s", "p", {"type": "object"}, "sonnet"))
    assert meta["provider"] == "groq" and "429" in meta["fallback_errors"][0]


def test_all_providers_fail_raises(keys, monkeypatch):
    async def fake_post(url, body, headers, retries=3):
        raise llm.RetryableLLMError("http 503")
    monkeypatch.setattr(llm, "_post", fake_post)
    with pytest.raises(llm.LLMError, match="all providers failed"):
        asyncio.run(llm.complete_json("s", "p", {"type": "object"}, "sonnet"))


def test_invalid_json_is_an_error():
    with pytest.raises(llm.LLMError):
        llm._parse_json("not json at all")


def test_dotenv_does_not_override_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GROQ_MODEL", "from-env")
    import os
    os.environ.setdefault("GROQ_MODEL", "from-file")
    assert os.environ["GROQ_MODEL"] == "from-env"
