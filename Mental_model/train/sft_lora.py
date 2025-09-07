"""Minimal LoRA SFT using TRL + PEFT.

- Base model: set via --base_model (default: meta/llama3-8b-instruct or local path)
- Data: data/sft_train.jsonl with fields {"instruction": str, "response": str}
- LoRA target modules: q_proj, k_proj, v_proj, o_proj
- Output: outputs/sft-adapter

Run example:
  python train/sft_lora.py --base_model meta/llama3-8b-instruct --epochs 1
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List, Dict

from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig


def load_sft(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            # backward compat: support prompt/response too
            inst = obj.get("instruction") or obj.get("prompt") or ""
            resp = obj.get("response") or obj.get("output") or ""
            if inst and resp:
                rows.append({"instruction": inst, "response": resp})
    return rows


def format_example(ex: Dict[str, str]) -> str:
    return f"[System]\n你是一名同理、务实的中文心理支持助手。避免诊断/药物建议。\n[User]\n{ex['instruction']}\n[Assistant]\n{ex['response']}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", type=str, default="meta/llama3-8b-instruct")
    parser.add_argument("--data", type=str, default="data/sft_train.jsonl")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--out_dir", type=str, default="outputs/sft-adapter")
    args = parser.parse_args()

    data_path = Path(args.data)
    rows = load_sft(str(data_path))
    if not rows:
        raise RuntimeError("No SFT data found.")

    texts = [format_example(r) for r in rows]
    ds = Dataset.from_dict({"text": texts})

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model, torch_dtype="auto", device_map="auto"
    )

    lora_cfg = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    sft_cfg = SFTConfig(
        output_dir=args.out_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=2,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=10,
        save_steps=1000,
        save_total_limit=1,
        fp16=True,
    )

    model = get_peft_model(model, lora_cfg)

    trainer = SFTTrainer(
        model=model,
        args=sft_cfg,
        train_dataset=ds,
        dataset_text_field="text",
        tokenizer=tokenizer,
        max_seq_length=1024,
    )
    trainer.train()
    trainer.model.save_pretrained(args.out_dir)
    tokenizer.save_pretrained(args.out_dir)


if __name__ == "__main__":
    main()
