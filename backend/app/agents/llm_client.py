"""Configurable Multi-Provider LLM Client for Autonomous Research Agents.
Supports OpenAI, Google Gemini, Anthropic Claude, and Local Ollama via standard HTTP.
Falls back gracefully to deterministic verification sandbox if no API key is provided.
"""
from __future__ import annotations
import os
import json
import logging
from typing import Dict, Any, Optional

import httpx

logger = logging.getLogger("llm_client")


class LLMClient:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "").strip()
        self.model = os.getenv("LLM_MODEL", "").strip()

    def is_configured(self) -> bool:
        """Returns True if any valid LLM provider API key or local Ollama endpoint is configured."""
        return bool(self.openai_key or self.gemini_key or self.anthropic_key or self.ollama_url)

    def get_provider_name(self) -> str:
        if self.openai_key:
            return f"OpenAI ({self.model or 'gpt-4o-mini'})"
        if self.gemini_key:
            return f"Google Gemini ({self.model or 'gemini-1.5-flash'})"
        if self.anthropic_key:
            return f"Anthropic ({self.model or 'claude-3-5-sonnet'})"
        if self.ollama_url:
            return f"Local Ollama ({self.ollama_url})"
        return "Deterministic Verification Sandbox (No API Key set)"

    async def generate_json(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Invokes the configured LLM and expects a JSON structured response."""
        if not self.is_configured():
            return None

        try:
            # 1. OpenAI Provider
            if self.openai_key:
                model = self.model or "gpt-4o-mini"
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.openai_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": model,
                            "response_format": {"type": "json_object"},
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            "temperature": 0.1
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["choices"][0]["message"]["content"]
                        return json.loads(content)
                    else:
                        logger.warning(f"OpenAI error {resp.status_code}: {resp.text}")

            # 2. Google Gemini Provider
            elif self.gemini_key:
                model = self.model or "gemini-1.5-flash"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(
                        url,
                        headers={"Content-Type": "application/json"},
                        json={
                            "contents": [
                                {"parts": [{"text": f"{system_prompt}\n\nTask:\n{user_prompt}\n\nRespond ONLY with a valid JSON object."}]}
                            ],
                            "generationConfig": {"response_mime_type": "application/json"}
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                        return json.loads(raw_text)

            # 3. Local Ollama
            elif self.ollama_url:
                model = self.model or "llama3.2"
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(
                        f"{self.ollama_url.rstrip('/')}/api/generate",
                        json={
                            "model": model,
                            "prompt": f"{system_prompt}\n\n{user_prompt}",
                            "format": "json",
                            "stream": False
                        }
                    )
                    if resp.status_code == 200:
                        return json.loads(resp.json()["response"])

        except Exception as e:
            logger.exception(f"Error calling LLM provider: {e}")

        return None


llm_client = LLMClient()
