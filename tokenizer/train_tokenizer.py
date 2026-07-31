"""
TinyGPT-10M — Tokenizer Trainer
Covers Chapters 6-10: Unicode, Tokenization, BPE, SentencePiece, Vocabulary

Usage:
    python tokenizer/train_tokenizer.py --input data/corpus.txt --vocab_size 8000
"""

import argparse
import os
import sentencepiece as spm


def train_tokenizer(input_file: str, model_prefix: str, vocab_size: int):
    """
    Trains a SentencePiece BPE tokenizer.

    model_type='bpe'   -> Byte Pair Encoding (Chapter 8)
    character_coverage  -> 1.0 recommended for non-English / mixed scripts (Hindi+English etc.)
                           since it ensures every Unicode char in corpus gets covered (Chapter 6)
    byte_fallback=True -> unknown chars fall back to raw bytes instead of <unk>,
                           so the tokenizer NEVER loses information (important for offline robustness)
    """
    spm.SentencePieceTrainer.train(
        input=input_file,
        model_prefix=model_prefix,
        vocab_size=vocab_size,
        model_type="bpe",
        character_coverage=1.0,
        byte_fallback=True,
        pad_id=0,
        unk_id=1,
        bos_id=2,
        eos_id=3,
        pad_piece="<pad>",
        unk_piece="<unk>",
        bos_piece="<s>",
        eos_piece="</s>",
    )
    print(f"Tokenizer saved: {model_prefix}.model / {model_prefix}.vocab")


class TinyTokenizer:
    """Thin wrapper so the rest of the codebase doesn't depend on sentencepiece's raw API directly."""

    def __init__(self, model_path: str):
        self.sp = spm.SentencePieceProcessor(model_file=model_path)

    @property
    def vocab_size(self):
        return self.sp.vocab_size()

    def encode(self, text: str, add_bos=False, add_eos=False):
        ids = self.sp.encode(text, out_type=int)
        if add_bos:
            ids = [self.sp.bos_id()] + ids
        if add_eos:
            ids = ids + [self.sp.eos_id()]
        return ids

    def decode(self, ids):
        return self.sp.decode(ids)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Path to raw text corpus (.txt)")
    parser.add_argument("--model_prefix", type=str, default="tokenizer/tinygpt_tokenizer")
    parser.add_argument("--vocab_size", type=int, default=8000)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.model_prefix) or ".", exist_ok=True)
    train_tokenizer(args.input, args.model_prefix, args.vocab_size)
