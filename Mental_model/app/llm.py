"""LLM client wrapper for Ollama.

Provides a simple chat() that composes system + memory + user messages.

TODOs:
- Add streaming if needed
- Add retries and better error handling
"""
from __future__ import annotations

import os
from typing import Optional

import httpx


def assemble_prompt(system: str, memory: str, user: str) -> str:
    memory_block = f"\nRelevant user memory:\n{memory}\n" if memory else ""
    return f"[System]\n{system}{memory_block}\n[User]\n{user}\n"


class LLMClient:
    def __init__(self, base_url: str, model_name: Optional[str] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name or os.getenv("MODEL_NAME", "llama3:instruct")
        # generation params
        self.temperature = float(os.getenv("GEN_TEMPERATURE", "0.2"))
        self.top_p = float(os.getenv("GEN_TOP_P", "0.9"))
        self.max_tokens = int(os.getenv("GEN_MAX_TOKENS", "512"))
        self._client = httpx.Client(timeout=60)

    def chat(self, system: str, user: str, memory: Optional[str] = None) -> str:
        prompt = assemble_prompt(system=system, memory=memory or "", user=user)
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "num_predict": self.max_tokens,
            "stream": False,
        }
        resp = self._client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")
