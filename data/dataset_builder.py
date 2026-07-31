"""
TinyGPT-10M — Dataset Builder + Data Loader
Covers Chapters 22-23: Dataset Builder, Data Loader

Two-step pipeline:
  1. build_binary(): tokenize a raw .txt corpus once, save as a flat uint16 binary file
     (this is the nanoGPT trick — avoids re-tokenizing every epoch, and memory-maps
     cleanly even for huge corpora that don't fit in RAM)
  2. TokenDataset: random-access windows into that binary file for training
"""

import os
import numpy as np
import torch
from torch.utils.data import Dataset


def build_binary(text_path: str, tokenizer, out_path: str, val_split: float = 0.1):
    """Tokenize the full corpus once and dump to train.bin / val.bin as uint16 arrays."""
    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    ids = tokenizer.encode(text)
    ids = np.array(ids, dtype=np.uint16)  # uint16 is enough since vocab_size < 65536

    n = len(ids)
    split_idx = int(n * (1 - val_split))
    train_ids, val_ids = ids[:split_idx], ids[split_idx:]

    os.makedirs(out_path, exist_ok=True)
    train_ids.tofile(os.path.join(out_path, "train.bin"))
    val_ids.tofile(os.path.join(out_path, "val.bin"))

    print(f"Total tokens: {n:,}")
    print(f"Train tokens: {len(train_ids):,} | Val tokens: {len(val_ids):,}")
    print(f"Saved to {out_path}/train.bin and {out_path}/val.bin")


class TokenDataset(Dataset):
    """
    Memory-maps the binary token file and returns random (x, y) windows of length block_size.
    y is x shifted by one position — that's the entire "next-token prediction" training objective.
    """

    def __init__(self, bin_path: str, block_size: int):
        self.data = np.memmap(bin_path, dtype=np.uint16, mode="r")
        self.block_size = block_size

    def __len__(self):
        return len(self.data) - self.block_size

    def __getitem__(self, idx):
        chunk = self.data[idx: idx + self.block_size + 1].astype(np.int64)
        x = torch.from_numpy(chunk[:-1])
        y = torch.from_numpy(chunk[1:])
        return x, y


def get_batch(dataset: TokenDataset, batch_size: int, device: str):
    """Simple random-sampling batcher (alternative to DataLoader for tight training loops)."""
    ix = torch.randint(len(dataset), (batch_size,))
    xs, ys = zip(*[dataset[i] for i in ix])
    x = torch.stack(xs).to(device, non_blocking=True)
    y = torch.stack(ys).to(device, non_blocking=True)
    return x, y


if __name__ == "__main__":
    import argparse
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    from tokenizer.train_tokenizer import TinyTokenizer

    parser = argparse.ArgumentParser()
    parser.add_argument("--text", type=str, required=True)
    parser.add_argument("--tokenizer_model", type=str, required=True)
    parser.add_argument("--out_dir", type=str, default="data/bin")
    args = parser.parse_args()

    tok = TinyTokenizer(args.tokenizer_model)
    build_binary(args.text, tok, args.out_dir)
