"""
TinyGPT-10M — Corpus Builder (Wikipedia, Hindi + English)

Wikipedia se articles stream karke ek combined .txt corpus banata hai.
Streaming mode use karta hai — poora Wikipedia dump download nahi karna padta,
sirf jitne articles chahiye utna hi fetch hota hai.

Requires internet (Colab/local machine pe chalega, is sandbox mein nahi).

Usage:
    python build_corpus.py --hi_articles 3000 --en_articles 3000 --out data/corpus.txt
"""

import argparse
import re
from datasets import load_dataset


def clean_text(text: str) -> str:
    """Halka cleanup — extra whitespace, reference markers wagaira hatana."""
    text = re.sub(r"\[\d+\]", "", text)          # [1], [2] jaise citation markers
    text = re.sub(r"\n{3,}", "\n\n", text)         # extra blank lines
    text = re.sub(r"[ \t]+", " ", text)            # multiple spaces
    return text.strip()


def collect_wikipedia(lang: str, n_articles: int, min_chars: int = 500) -> list[str]:
    """
    lang: 'hi' ya 'en'
    Streaming=True -> articles ek-ek karke aate hain, poora dataset RAM mein nahi aata.
    """
    print(f"Streaming Wikipedia [{lang}] ...")
    ds = load_dataset(
        "wikimedia/wikipedia", f"20231101.{lang}", split="train", streaming=True
    )

    texts = []
    for i, row in enumerate(ds):
        if len(texts) >= n_articles:
            break
        text = clean_text(row["text"])
        if len(text) >= min_chars:   # bahut chhote/stub articles skip karo
            texts.append(text)
        if (i + 1) % 500 == 0:
            print(f"  scanned {i+1} articles, collected {len(texts)}")

    print(f"[{lang}] collected {len(texts)} articles")
    return texts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hi_articles", type=int, default=3000)
    parser.add_argument("--en_articles", type=int, default=3000)
    parser.add_argument("--min_chars", type=int, default=500)
    parser.add_argument("--out", type=str, default="data/corpus.txt")
    args = parser.parse_args()

    all_texts = []
    if args.hi_articles > 0:
        all_texts += collect_wikipedia("hi", args.hi_articles, args.min_chars)
    if args.en_articles > 0:
        all_texts += collect_wikipedia("en", args.en_articles, args.min_chars)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_texts))

    total_chars = sum(len(t) for t in all_texts)
    print(f"\nDone. {len(all_texts)} articles, ~{total_chars/1e6:.1f}M characters written to {args.out}")


if __name__ == "__main__":
    main()
