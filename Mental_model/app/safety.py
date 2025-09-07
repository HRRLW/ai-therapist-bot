"""Safety module: crisis detection, moderation, and emotion intensity scoring.

TODOs:
- Expand crisis/violence keyword lists and add locale-specific variants
- Replace emotion_intensity_score with small ONNX/logreg model
- Integrate escalation workflow (hotline numbers, contacts)
"""
from __future__ import annotations

import json
import os
from typing import List, Tuple


CRISIS_KEYWORDS = [
    # Chinese
    "自杀", "结束生命", "自残", "割腕", "跳楼", "服药过量", "活不下去", "不想活了", "轻生", "活着没意义",
    # English
    "suicide", "kill myself", "end my life", "self harm", "cut myself", "overdose", "jump off", "i want to die",
]

MODERATION_BLOCKLIST = [
    "仇恨",
    "暴力威胁",
]

DBT_ROUTE_KEYWORDS = [
    "情绪失控",
    "爆发",
    "冲动",
    "强烈情绪",
    "崩溃",
]

_GUARD_TERMS = [
    "诊断",
    "处方",
    "药量",
    "药名",
    "百分百保证",
]

_DEF_CRISIS_MSG = "我注意到你提到了潜在的危机内容。请立刻联系本地紧急援助或可信赖的人，我们也建议致电当地心理援助热线。"


def _load_crisis_message() -> str:
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "conf", "safety_zh.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            msg = data.get("crisis_message_zh") or _DEF_CRISIS_MSG
            return msg
    except Exception:
        return _DEF_CRISIS_MSG


CRISIS_MESSAGE = _load_crisis_message()


def is_crisis(text: str) -> bool:
    return any(kw.lower() in text.lower() for kw in CRISIS_KEYWORDS)


def crisis_detector(text: str) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    for kw in CRISIS_KEYWORDS:
        if kw.lower() in text.lower():
            reasons.append(f"hit:{kw}")
    return (len(reasons) > 0, reasons)


def moderation_filter(text: str) -> Tuple[bool, List[str]]:
    reasons: List[str] = []
    for kw in MODERATION_BLOCKLIST:
        if kw in text:
            reasons.append(f"blocked:{kw}")
    allowed = len(reasons) == 0
    return allowed, reasons


def emotion_intensity_score(text: str) -> float:
    # Stub: constant default 0.5; replace with scikit model later
    return 0.5


def guard_output(reply: str) -> str:
    """Post-generation guard: replace unsafe medical/diagnostic content.

    If reply contains terms like diagnosis/prescription/med dosage/drug names/"100% guarantee",
    replace the entire reply with a safe, action-focused fallback.
    """
    lower = reply.lower()
    if any(term in reply for term in _GUARD_TERMS):
        return "抱歉，我不能提供诊断或药物建议，我们可以先聚焦一个可执行的小步骤。"
    # Also check common English terms
    en_terms = ["diagnosis", "prescription", "dosage", "mg ", "% guarantee", "100% guarantee"]
    if any(t in lower for t in en_terms):
        return "抱歉，我不能提供诊断或药物建议，我们可以先聚焦一个可执行的小步骤。"
    return reply
