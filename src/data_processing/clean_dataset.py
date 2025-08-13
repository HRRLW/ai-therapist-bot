
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_dataset.py
----------------
Fix common mojibake in Reddit-style CSV exports (e.g., “I‚Äôm” -> “I'm”),
normalize quotes/whitespace, and write a clean CSV next to the input file.

Default paths match your tree:
- input:  Data/Depression_Dataset/dataset.csv
- output: Data/Depression_Dataset/dataset_clean.csv

Usage:
    python clean_dataset.py \
        --input Data/Depression_Dataset/dataset.csv

    # Or specify output:
    python clean_dataset.py \
        --input Data/Depression_Dataset/dataset.csv \
        --output Data/Depression_Dataset/dataset_clean.csv
"""
import argparse
import os
import re
import unicodedata
import pandas as pd

try:
    from ftfy import fix_text  # pip install ftfy
except Exception:
    fix_text = None

def _default_input():
    here = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(here, ".."))  # src/
    project_root = os.path.abspath(os.path.join(project_root, ".."))  # project root
    return os.path.join(project_root, "Data", "Depression_Dataset", "dataset.csv")

def normalize_text(s: str) -> str:
    if not isinstance(s, str):
        s = "" if pd.isna(s) else str(s)

    # 1) Fix mojibake via ftfy if available
    if fix_text:
        s = fix_text(s)

    # 2) Manual quick fixes (covers common cases if ftfy not installed)
    replacements = {
        "â€™": "'", "â€˜": "'", "â€œ": '"', "â€": '"', "â€”": "-",
        "â€“": "-", "Â ": " ", "â€¦": "...",
        "‚Äô": "'", "‚Ä¶": "...", "‚Äì": "-", "â€": '"', "Ã©": "é",
        "Ã±": "ñ", "Ã¼": "ü", "Ã¶": "ö", "Ã¤": "ä", "Ã": "à"  # generic fallbacks
    }
    for k, v in replacements.items():
        s = s.replace(k, v)

    # 3) Normalize Unicode (NFKC)
    s = unicodedata.normalize("NFKC", s)

    # 4) Collapse excessive whitespace
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s+\n", "\n", s)
    return s.strip()

def clean_dataframe(df: pd.DataFrame, text_cols=("title", "content")) -> pd.DataFrame:
    cleaned = df.copy()
    for col in text_cols:
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].map(normalize_text)
    return cleaned

def main():
    ap = argparse.ArgumentParser("Clean mojibake in CSV and write a clean copy.")
    ap.add_argument("--input", "-i", default=_default_input(), help="Path to input CSV")
    ap.add_argument("--output", "-o", default=None, help="Path to output CSV (default: <input_dir>/dataset_clean.csv)")
    ap.add_argument("--title-col", default="title")
    ap.add_argument("--content-col", default="content")
    args = ap.parse_args()

    in_path = args.input
    if args.output is None:
        out_path = os.path.join(os.path.dirname(os.path.abspath(in_path)), "dataset_clean.csv")
    else:
        out_path = args.output

    print("[INFO] Reading:", os.path.abspath(in_path))
    df = pd.read_csv(in_path)

    cleaned = clean_dataframe(df, text_cols=(args.title_col, args.content_col))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cleaned.to_csv(out_path, index=False)
    print("[OK] Cleaned CSV saved to:", os.path.abspath(out_path))
    print("[INFO] Rows:", len(cleaned), "| Columns:", list(cleaned.columns))

if __name__ == "__main__":
    main()
