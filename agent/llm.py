"""LLM backends. Both make real model calls; neither fabricates output.

- claude-cli : the Claude Code CLI in headless mode (`claude -p`). Uses the
               logged-in Claude account; reports real cost per call.
- anthropic  : the Anthropic Messages API (needs ANTHROPIC_API_KEY).
Set ATLAS_LLM=claude-cli|anthropic and CLAUDE_BIN to override the CLI path.
"""
from __future__ import annotations

import asyncio, json, os, re, shutil

import httpx


class LLMError(RuntimeError):
    pass


def backend() -> str:
    b = os.environ.get("ATLAS_LLM")
    if b:
        return b
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "claude-cli"


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
    """Return (parsed_json, meta{cost_usd, model, turns})."""
    if backend() == "anthropic":
        if tools:
            raise LLMError("web tools are only wired for the claude-cli backend")
        return await _anthropic(system, prompt, schema, model)
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
