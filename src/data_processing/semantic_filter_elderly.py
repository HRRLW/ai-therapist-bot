
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
semantic_filter_elderly.py
==========================

使用“LLM 语义过滤”从抑郁相关数据集中筛选“老年人自述 / 老年相关场景”的文本。
本脚本具备以下特性：
1) **从 `config/.env` 读取 API Key/模型等配置**（使用 python-dotenv）
2) **关键词 + 年龄正则预筛** → 明显不相关的跳过大模型，降低成本
3) **OpenAI 兼容接口**：可使用 OpenAI / DeepSeek / 其他兼容 OpenAI 的服务
4) **严格 JSON 输出**：`{"label": "elderly|not_elderly|uncertain", "confidence": 0-1, "reason": "..."}`
5) **断点续跑**：已写入的行不会重复请求
6) **双输出**：保存全部结果，以及按置信度阈值筛出的高置信子集
7) **路径友好**：默认读取 `Data/Depression_Dataset/dataset_clean.csv`（若不存在则用 `dataset.csv`），
   默认输出到同目录下 `elderly_llm_filtered.csv` 与 `elderly_llm_filtered_confident.csv`。

依赖：
- pandas
- python-dotenv (用于加载 config/.env)
- （可选）requests；这里用内置 urllib，避免额外依赖

示例用法：
    # 先在 config/.env 中配置：
    # LLM_API_KEY=sk-xxx
    # LLM_API_BASE=https://api.openai.com/v1
    # LLM_MODEL=gpt-4o-mini

    # 直接运行（自动选择 clean 或 raw）
    python src/data_processing/semantic_filter_elderly.py

    # 指定输入输出与置信度阈值
    python src/data_processing/semantic_filter_elderly.py \
        --input Data/Depression_Dataset/dataset_clean.csv \
        --output Data/Depression_Dataset/elderly_llm_filtered.csv \
        --min-confidence 0.6
"""

from __future__ import annotations
import os
import re
import csv
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List

import pandas as pd
from dotenv import load_dotenv

# -------------------------------
# 读取配置：从项目根目录的 config/.env
# -------------------------------
def load_env_from_config() -> None:
    """
    优先从 <project_root>/config/.env 加载；若不存在，再尝试当前工作目录。
    """
    here = Path(__file__).resolve()
    project_root = here.parents[2]  # data_processing -> src -> <project_root>
    env_path = project_root / "config" / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)  # 不覆盖现有环境变量
    else:
        # 兜底：尝试当前工作目录下的 .env（有时用户会把 .env 放在根目录）
        load_dotenv(override=False)

load_env_from_config()

# -------------------------------
# OpenAI 兼容 API 配置（可在 .env 覆盖）
# -------------------------------
DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
API_KEY = os.getenv("LLM_API_KEY", "")
API_BASE = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")

# -------------------------------
# 轻量 HTTP 客户端（内置 urllib）
# -------------------------------
import urllib.request

def _http_post(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    向 OpenAI 兼容的 /chat/completions 发送 POST 请求。
    说明：此实现不依赖第三方库，若你偏好 requests，可自行替换。
    """
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)

def call_chat_json(messages: List[Dict[str, str]], model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    请求 Chat Completions，并强制返回 JSON（依赖 response_format）。
    """
    url = f"{API_BASE}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
    }
    payload = {
        "model": model,
        "temperature": 0,  # 语义分类任务宜使用 0，保证确定性
        "response_format": {"type": "json_object"},
        "messages": messages,
    }
    return _http_post(url, headers, payload)

# -------------------------------
# 预筛：关键词 / 年龄模式，降低成本
# -------------------------------
EN_HINTS = [
    "elderly","senior","older adult","grandma","grandpa","aging parent",
    "nursing home","retirement home","assisted living","dementia","alzheimer","parkinson",
    "65-year-old","70-year-old"
]
CN_HINTS = [
    "老人","老年","长者","独居老人","空巢老人","养老院","老人院","护理院","赡养","看护",
    "照护","失智","阿尔茨海默","帕金森","高龄","爷爷","奶奶","外公","外婆","祖父","祖母","岁"
]

def maybe_elderly(text: str) -> bool:
    """
    返回 True 表示“可能与老年相关”，再交给 LLM 精筛；否则可直接判为 not_elderly（低置信）。
    """
    low = text.lower()
    # 英文关键词
    for k in EN_HINTS:
        if k in low:
            return True
    # 中文关键词
    for k in CN_HINTS:
        if k in text:
            return True
    # 年龄正则（英文）
    if re.search(r"\\b([6-9]\\d)\\s*(?:year|yrs|yo|y/o)?[- ]?old\\b", low):
        return True
    # 年龄正则（中文）
    if re.search(r"([6-9]\\d)\\s*岁", text):
        return True
    return False

# -------------------------------
# LLM 提示词（尽量简洁、可复用）
# -------------------------------
SYSTEM_PROMPT = (
    "You are a precise classifier. Determine if a text is about "
    "*elderly self-disclosure or elderly-related scenarios*. "
    "Return only JSON with: label, confidence (0-1), reason (<=30 words)."
)

USER_INSTRUCTIONS = (
    "Classify TEXT into one of three labels:\\n"
    "- \"elderly\": elderly self-disclosure (age >=60) OR elderly-care scenario (e.g., nursing home, dementia).\\n"
    "- \"not_elderly\": unrelated to elderly.\\n"
    "- \"uncertain\": insufficient info.\\n\\n"
    "TEXT:\\n{TEXT}"
)

# -------------------------------
# 主流程：读取数据 → 预筛 → LLM 分类 → 写出结果
# -------------------------------
def run(input_path: Path, output_path: Path, min_conf: float) -> None:
    """
    :param input_path: 输入 CSV，需包含 'title' 和 'content' 列
    :param output_path: 输出 CSV，保存分类结果（含 label/confidence/reason/title/content）
    :param min_conf: 生成高置信子集时的阈值（只保留 label=elderly 且 confidence>=阈值 的行）
    """
    if not API_KEY:
        raise SystemExit("[ERROR] 未检测到 API Key。请在 config/.env 中设置 LLM_API_KEY。")

    # 读取数据
    df = pd.read_csv(input_path)
    if "title" not in df.columns or "content" not in df.columns:
        raise SystemExit(f"[ERROR] CSV 必须包含 'title' 和 'content' 列。实际为：{list(df.columns)}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 断点续跑：收集已完成的行号
    done_ids = set()
    if output_path.exists():
        with output_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    done_ids.add(int(row["row_id"]))
                except Exception:
                    pass

    with output_path.open("a", newline="", encoding="utf-8") as f:
        writer = None

        for i, row in df.iterrows():
            if i in done_ids:
                continue

            title = str(row.get("title", "") or "")
            content = str(row.get("content", "") or "")
            text = f"{title}\n\n{content}".strip()

            # ---------- 预筛：明显不相关则跳过 LLM ----------
            if not maybe_elderly(text):
                out = {
                    "row_id": i,
                    "label": "not_elderly",
                    "confidence": 0.3,  # 低置信以示启发式判断
                    "reason": "keyword prefilter negative",
                    "title": title,
                    "content": content,
                }
            else:
                # ---------- 调用 LLM：严格 JSON 输出 ----------
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_INSTRUCTIONS.format(TEXT=text[:4000])},
                ]
                # 简单重试（指数退避）
                for attempt in range(5):
                    try:
                        resp = call_chat_json(messages)
                        content_json = resp["choices"][0]["message"]["content"]
                        parsed = json.loads(content_json)  # 依赖 response_format 的 JSON 输出
                        out = {
                            "row_id": i,
                            "label": parsed.get("label", "uncertain"),
                            "confidence": float(parsed.get("confidence", 0)),
                            "reason": parsed.get("reason", ""),
                            "title": title,
                            "content": content,
                        }
                        break
                    except Exception as e:
                        wait = 2 ** attempt
                        print(f"[WARN] API error: {e}; retry in {wait}s")
                        time.sleep(wait)
                else:
                    # 多次失败则标记为不确定
                    out = {
                        "row_id": i,
                        "label": "uncertain",
                        "confidence": 0.0,
                        "reason": "API failed",
                        "title": title,
                        "content": content,
                    }

            # 首次写入时创建表头
            if writer is None:
                writer = csv.DictWriter(f, fieldnames=list(out.keys()))
                if output_path.stat().st_size == 0:
                    writer.writeheader()
            writer.writerow(out)

    # 生成“高置信子集”文件，便于直接使用
    all_df = pd.read_csv(output_path)
    subset = all_df[(all_df["label"] == "elderly") & (all_df["confidence"] >= min_conf)]
    subset_path = output_path.parent / "elderly_llm_filtered_confident.csv"
    subset.to_csv(subset_path, index=False)

    print(f"[OK] 完整结果: {output_path}")
    print(f"[OK] 高置信子集(>= {min_conf}): {subset_path}")

# -------------------------------
# CLI：解析参数并运行
# -------------------------------
def default_io_paths() -> tuple[Path, Path]:
    """
    根据你的目录结构自动推导默认输入/输出路径：
    - 优先使用 Data/Depression_Dataset/dataset_clean.csv
    - 否则使用 Data/Depression_Dataset/dataset.csv
    - 输出到同目录 elderly_llm_filtered.csv
    """
    here = Path(__file__).resolve()
    project_root = here.parents[2]
    base = project_root / "Data" / "Depression_Dataset"
    in_clean = base / "dataset_clean.csv"
    in_raw = base / "dataset.csv"
    input_path = in_clean if in_clean.exists() else in_raw
    output_path = base / "elderly_llm_filtered.csv"
    return input_path, output_path

def main():
    inp_default, out_default = default_io_paths()

    ap = argparse.ArgumentParser(description="LLM 语义过滤（老年相关）")
    ap.add_argument("--input", "-i", default=str(inp_default), help="输入 CSV（含 title/content 列）")
    ap.add_argument("--output", "-o", default=str(out_default), help="输出结果 CSV")
    ap.add_argument("--min-confidence", type=float, default=0.6, help="高置信子集阈值（默认 0.6）")
    args = ap.parse_args()

    run(Path(args.input), Path(args.output), args.min_confidence)

if __name__ == "__main__":
    main()
