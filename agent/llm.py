"""LLM providers. Every provider makes a real model call; none fabricates output.

- gemini     : Google Gemini API (GEMINI_API_KEY, model GEMINI_MODEL).
- groq       : GroqCloud OpenAI-compatible API (GROQ_API_KEY, model GROQ_MODEL).
- anthropic  : Anthropic Messages API (ANTHROPIC_API_KEY).
- claude-cli : Claude Code CLI in headless mode (`claude -p`), logged-in account.

ATLAS_LLM (or AI_PROVIDER) = auto | gemini | groq | anthropic | claude-cli.
`auto` tries, in order, every provider whose credentials exist and falls back to
the next one on quota/rate-limit/server errors. Web-search tools (used by the
independent pass B) are only available on claude-cli; Gemini/Groq are used for
grounded extraction over pages our own fetcher retrieved.
Keys are read from the environment or a git-ignored .env file; never logged.
"""
from __future__ import annotations

import asyncio, json, os, re, shutil

import httpx


class LLMError(RuntimeError):
    pass


def _load_dotenv():
    """Minimal .env loader (KEY=VALUE lines); existing env vars win."""
    from pathlib import Path
    p = Path(__file__).resolve().parent.parent / ".env"
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()


def available() -> list[str]:
    """Providers with credentials, in fallback priority order."""
    out = []
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        out.append("gemini")
    if os.environ.get("GROQ_API_KEY"):
        out.append("groq")
    if os.environ.get("ANTHROPIC_API_KEY"):
        out.append("anthropic")
    if shutil.which(claude_bin()) or os.path.exists(claude_bin()):
        out.append("claude-cli")
    return out


def chain(tools: list[str] | None = None) -> list[str]:
    b = (os.environ.get("ATLAS_LLM") or os.environ.get("AI_PROVIDER") or "auto").lower()
    provs = available() if b == "auto" else [b]
    if tools:  # web-search tools only exist on claude-cli
        provs = [p for p in provs if p == "claude-cli"] or ["claude-cli"]
    return provs or ["claude-cli"]


def backend() -> str:
    return chain()[0]


class RetryableLLMError(LLMError):
    """Quota / rate limit / server error: the next provider may succeed."""


# Defaults verified available on 2026-11-23 via each API's model list; overridable.
GEMINI_DEFAULT = "gemini-3.5-flash"
GROQ_DEFAULT = "openai/gpt-oss-120b"


def _schema_hint(schema: dict) -> str:
    return ("Return ONLY a JSON object that validates against this JSON Schema "
            "(no prose, no code fences):\n" + json.dumps(schema)[:12000])


async def _post(url, body, headers, retries=3):
    async with httpx.AsyncClient(timeout=180) as c:
        for attempt in range(retries + 1):
            try:
                r = await c.post(url, json=body, headers=headers)
            except httpx.HTTPError as e:  # timeouts, connection resets
                if attempt < retries:
                    await asyncio.sleep(5); continue
                raise RetryableLLMError(f"{type(e).__name__}: {e}")
            if r.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                await asyncio.sleep(min(60, 5 * 2 ** attempt))
                continue
            break
    if r.status_code in (429, 500, 502, 503, 504):
        raise RetryableLLMError(f"http {r.status_code}: {r.text[:200]}")
    if r.status_code != 200:
        raise LLMError(f"http {r.status_code}: {r.text[:300]}")
    return r.json()


async def _gemini(system, prompt, schema, model):
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    mid = os.environ.get("GEMINI_MODEL") or GEMINI_DEFAULT
    j = await _post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{mid}:generateContent",
        {"systemInstruction": {"parts": [{"text": system}]},
         "contents": [{"role": "user", "parts": [{"text": prompt + "\n\n" + _schema_hint(schema)}]}],
         "generationConfig": {"responseMimeType": "application/json", "temperature": 0}},
        {"x-goog-api-key": key})
    try:
        text = "".join(p.get("text", "") for p in j["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError):
        raise LLMError(f"gemini returned no content: {str(j)[:200]}")
    u = j.get("usageMetadata", {})
    return _parse_json(text), {"cost_usd": None, "model": f"gemini/{mid}", "turns": 1,
                               "tokens_in": u.get("promptTokenCount"), "tokens_out": u.get("candidatesTokenCount")}


async def _groq(system, prompt, schema, model):
    mid = os.environ.get("GROQ_MODEL") or GROQ_DEFAULT
    j = await _post(
        "https://api.groq.com/openai/v1/chat/completions",
        {"model": mid, "temperature": 0, "response_format": {"type": "json_object"},
         "messages": [{"role": "system", "content": system},
                      {"role": "user", "content": prompt + "\n\n" + _schema_hint(schema)}]},
        {"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}"})
    u = j.get("usage", {})
    return _parse_json(j["choices"][0]["message"]["content"]), {
        "cost_usd": None, "model": f"groq/{mid}", "turns": 1,
        "tokens_in": u.get("prompt_tokens"), "tokens_out": u.get("completion_tokens")}


def claude_bin() -> str:
    return (os.environ.get("CLAUDE_BIN") or shutil.which("claude")
            or os.environ.get("CLAUDE_CODE_EXECPATH") or "claude")


def _parse_json(text: str) -> dict:
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    raw = m.group(1) if m else text[text.find("{"): text.rfind("}") + 1]
    try:
        return json.loads(raw)
    except Exception as e:
        raise LLMError(f"invalid JSON from model: {e}; head={text[:200]!r}")


async def complete_json(system: str, prompt: str, schema: dict, model: str,
                        tools: list[str] | None = None, timeout: int = 600,
                        max_turns: int = 30) -> tuple[dict, dict]:
    """Return (parsed_json, meta). Tries each provider in chain(); falls back on
    retryable errors (quota, rate limit, 5xx) and records which provider answered."""
    errors = []
    for prov in chain(tools):
        try:
            if prov == "gemini":
                data, meta = await _gemini(system, prompt, schema, model)
            elif prov == "groq":
                data, meta = await _groq(system, prompt, schema, model)
            elif prov == "anthropic":
                data, meta = await _anthropic(system, prompt, schema, model)
            else:
                data, meta = await _claude_cli(system, prompt, schema, model, tools, timeout, max_turns)
            meta["provider"] = prov
            meta["fallback_errors"] = errors
            return data, meta
        except RetryableLLMError as e:
            errors.append(f"{prov}: {e}")
            continue
        except LLMError as e:
            errors.append(f"{prov}: {e}")
            if prov == chain(tools)[-1]:
                break
            continue
    raise LLMError("all providers failed: " + " | ".join(errors))


async def _claude_cli(system, prompt, schema, model, tools, timeout, max_turns):
    cmd = [claude_bin(), "-p", "--output-format", "json", "--model", model,
           "--system-prompt", system, "--json-schema", json.dumps(schema),
           "--setting-sources", "", "--strict-mcp-config",
           "--max-turns", str(max_turns),
           "--tools", ",".join(tools) if tools else ""]
    if tools:
        cmd += ["--allowedTools", ",".join(tools)]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, cwd=os.environ.get("TMPDIR", "/tmp"))
    try:
        out, err = await asyncio.wait_for(proc.communicate(prompt.encode()), timeout)
    except asyncio.TimeoutError:
        proc.kill()
        raise LLMError(f"claude-cli timed out after {timeout}s")
    try:
        env = json.loads(out.decode())
    except Exception:
        raise LLMError(f"claude-cli bad output rc={proc.returncode}: {out[:200]!r} {err[:200]!r}")
    if env.get("is_error"):
        raise LLMError(f"claude-cli error: {str(env.get('result'))[:300]}")
    data = env.get("structured_output") or _parse_json(env.get("result") or "")
    meta = {"cost_usd": env.get("total_cost_usd"), "model": model,
            "turns": env.get("num_turns"),
            "web_searches": (env.get("usage", {}).get("server_tool_use") or {}).get("web_search_requests")}
    return data, meta


# USD per million tokens (input, output) for cost accounting on the API backend.
_PRICES = {"sonnet": (3.0, 15.0), "haiku": (1.0, 5.0), "opus": (5.0, 25.0)}
_IDS = {"sonnet": "claude-sonnet-5-5", "haiku": "claude-haiku-5-5", "opus": "claude-opus-5-5"}


async def _anthropic(system, prompt, schema, model):
    key = os.environ["ANTHROPIC_API_KEY"]
    mid = _IDS.get(model, model)
    body = {"model": mid, "max_tokens": 8000, "system": system,
            "tools": [{"name": "submit", "description": "Submit the research result",
                       "input_schema": schema}],
            "tool_choice": {"type": "tool", "name": "submit"},
            "messages": [{"role": "user", "content": prompt}]}
    async with httpx.AsyncClient(timeout=300) as c:
        for attempt in range(4):
            r = await c.post("https://api.anthropic.com/v1/messages", json=body, headers={
                "x-api-key": key, "anthropic-version": "2023-06-01"})
            if r.status_code in (429, 529, 500) and attempt < 3:
                await asyncio.sleep(5 * (attempt + 1)); continue
            break
    if r.status_code != 200:
        raise LLMError(f"anthropic http {r.status_code}: {r.text[:300]}")
    j = r.json()
    data = next(b["input"] for b in j["content"] if b["type"] == "tool_use")
    pin, pout = next((v for k, v in _PRICES.items() if k in mid), (3.0, 15.0))
    u = j["usage"]
    cost = (u["input_tokens"] * pin + u["output_tokens"] * pout) / 1e6
    return data, {"cost_usd": round(cost, 5), "model": mid, "turns": 1}
