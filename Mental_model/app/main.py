"""FastAPI entrypoint for the lightweight psych support bot.

Pipeline (/chat POST):
- Safety: crisis detection -> moderation filter -> emotion intensity scoring
- Memory: recall top-k memories
- Policy routing: DBT on keywords, otherwise CBT
- LLM: compose system + memory + user, call Ollama
- Memory writeback: store interaction

TODOs:
- Replace emotion_intensity_classifier with a trained model or ONNX
- Extend moderation rules and crisis escalation hooks
- Add session management and better memory schemas
"""
from __future__ import annotations

import os
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .llm import LLMClient
from .memory import MemoryStore, MemoryItem, extract_memory_points
from .safety import crisis_detector, moderation_filter, emotion_intensity_score, guard_output, CRISIS_MESSAGE
from .policies import get_policy_prompt, route_policy

load_dotenv()

app = FastAPI(title="Mental Model Demo", version="0.1.3")


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="User unique id")
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Optional session id")


class ChatResponse(BaseModel):
    response: str
    policy: str
    blocked: bool
    reasons: List[str]
    memory_ids: List[str]
    emotion_intensity: float


# Environment/config
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3:instruct")
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", MODEL_NAME)
CHROMA_HOST = os.getenv("CHROMA_HOST", "").strip()
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
MEMORY_TOP_K = int(os.getenv("MEMORY_TOP_K", "4"))

# Services
llm_client = LLMClient(base_url=OLLAMA_BASE_URL, model_name=MODEL_NAME)
memory = MemoryStore(
    persist_dir=CHROMA_PERSIST_DIR,
    host=CHROMA_HOST or None,
    embed_model_name=EMBED_MODEL_NAME,
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    # 1) Crisis detection first
    crisis, crisis_reasons = crisis_detector(req.message)
    if crisis:
        return ChatResponse(
            response=CRISIS_MESSAGE,
            policy="CRISIS",
            blocked=True,
            reasons=crisis_reasons,
            memory_ids=[],
            emotion_intensity=1.0,
        )

    # 2) Moderation filter
    allowed, mod_reasons = moderation_filter(req.message)
    if not allowed:
        return ChatResponse(
            response="抱歉，这条信息包含不适宜的内容，我无法继续回应。",
            policy="BLOCKED",
            blocked=True,
            reasons=mod_reasons,
            memory_ids=[],
            emotion_intensity=0.0,
        )

    # 3) Emotion intensity score
    intensity = emotion_intensity_score(req.message)

    # 4) Recall memory (top-k)
    recalled = memory.recall(user_id=req.user_id, query=req.message, k=MEMORY_TOP_K)
    memory_context = "\n".join([f"- {m.text}" for m in recalled]) if recalled else ""

    # 5) Policy routing -> system prompt
    policy = route_policy(req.message)
    system_prompt = get_policy_prompt(policy)

    # 6) Call LLM
    assistant = llm_client.chat(
        system=system_prompt,
        user=req.message,
        memory=memory_context,
    )
    assistant = guard_output(assistant)

    # 7) Write memory after successful generation: only key points
    memory_ids: List[str] = []
    try:
        for point in extract_memory_points(f"user: {req.message}\nassistant: {assistant}"):
            memory_ids.append(memory.add_snapshot(user_id=req.user_id, text=point))
    except Exception:
        memory_ids = []

    return ChatResponse(
        response=assistant,
        policy=policy,
        blocked=False,
        reasons=[],
        memory_ids=memory_ids,
        emotion_intensity=float(intensity),
    )
