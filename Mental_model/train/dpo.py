"""Minimal DPO script stub.

Data: data/dpo_train.jsonl with fields {"prompt": str, "chosen": str, "rejected": str}
This demo only loads and prints dataset size; integrate TRL's DPOTrainer as needed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Dict

from datasets import Dataset


def load_dpo(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            p = obj.get("prompt", "")
            c = obj.get("chosen", "")
            r = obj.get("rejected", "")
            if p and c and r:
                rows.append({"prompt": p, "chosen": c, "rejected": r})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default="data/dpo_train.jsonl")
    args = parser.parse_args()

    data_path = Path(args.data)
    rows = load_dpo(str(data_path))
    if not rows:
        raise RuntimeError("No DPO data found.")

    ds = Dataset.from_list(rows)
    print(f"Loaded DPO pairs: {len(ds)}. Integrate TRL DPOTrainer here.")


if __name__ == "__main__":
    main()
