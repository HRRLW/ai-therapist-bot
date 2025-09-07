"""Chroma-based long-term memory store.

Provides basic add_snapshot(user_id, text) and recall(user_id, query, k) APIs.

TODOs:
- Add metadata schema (timestamps, session ids)
- Replace embedding with local embedding later
"""
from __future__ import annotations

import os
import re
import uuid
from typing import List, Optional

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions


class MemoryItem:
    def __init__(self, text: str, id: Optional[str] = None) -> None:
        self.id = id or str(uuid.uuid4())
        self.text = text


class MemoryStore:
    def __init__(
        self,
        persist_dir: str = "./chroma_db",
        host: Optional[str] = None,
        embed_model_name: str = "default",
        collection_name: str = "long_term_memory",
    ) -> None:
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        if host:
            self.client = chromadb.HttpClient(host=host)
        else:
            os.makedirs(persist_dir, exist_ok=True)
            self.client = chromadb.Client(
                Settings(is_persistent=True, persist_directory=persist_dir)
            )
        # Default embedding; replace later with local embedding
        self.embed_fn = embedding_functions.DefaultEmbeddingFunction()
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name, embedding_function=self.embed_fn
            )
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name, embedding_function=self.embed_fn
            )

    def add_snapshot(self, user_id: str, text: str) -> str:
        item = MemoryItem(text=text)
        self.collection.add(
            ids=[item.id], documents=[item.text], metadatas=[{"user_id": user_id}]
        )
        return item.id

    def recall(self, user_id: str, query: str, k: int = 4) -> List[MemoryItem]:
        results = self.collection.query(
            query_texts=[query], n_results=k, where={"user_id": user_id}
        )
        docs = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]
        return [MemoryItem(text=t, id=i) for i, t in zip(ids, docs)]

    # Back-compat wrappers
    def add(self, user_id: str, items: List[MemoryItem]) -> List[str]:
        ids = []
        for it in items:
            ids.append(self.add_snapshot(user_id=user_id, text=it.text))
        return ids

    def query(self, user_id: str, query_text: str, top_k: int = 4) -> List[MemoryItem]:
        return self.recall(user_id=user_id, query=query_text, k=top_k)


def extract_memory_points(text: str) -> List[str]:
    """Extract concise memory points from dialogue text.

    Heuristics:
    - Keep only lines/sentences that mention goals, triggers, or weekly homework.
    - Chinese/English keywords: 目标/想要/希望, 触发/诱因/trigger, 作业/练习/本周/homework.
    - Deduplicate and trim length.
    """
    if not text:
        return []

    # Split by line or sentence punctuation
    parts = re.split(r"[\n。！？!?]+", text)
    keywords = [
        r"目标|想要|希望|goal",
        r"触发|诱因|trigger",
        r"作业|练习|本周|homework",
    ]
    pattern = re.compile("(" + ")|(".join(keywords) + ")", re.IGNORECASE)

    candidates: List[str] = []
    for p in parts:
        s = p.strip()
        if not s:
            continue
        if pattern.search(s):
            # Normalize whitespace and cap length
            s = re.sub(r"\s+", " ", s)
            if len(s) > 200:
                s = s[:200] + "…"
            candidates.append(s)

    # Deduplicate preserving order
    seen = set()
    out: List[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out
