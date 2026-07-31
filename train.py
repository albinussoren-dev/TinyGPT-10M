"""
TinyGPT-10M — Training Script
Covers Chapters 24-28: Training Loop, Optimizer, Scheduler, Checkpoints, Validation

Usage:
    python train.py --data_dir data/bin --out_dir checkpoints
"""

import argparse
import math
import os
import time

import torch

from config import TinyGPTConfig
from model import TinyGPT
from data.dataset_builder import TokenDataset, get_batch


def get_lr(it, cfg: TinyGPTConfig):
    """Chapter 26: cosine decay schedule with linear warmup — the GPT-3 recipe."""
    if it < cfg.warmup_iters:
        return cfg.learning_rate * (it + 1) / cfg.warmup_iters
    if it > cfg.max_iters:
        return cfg.min_lr
    decay_ratio = (it - cfg.warmup_iters) / (cfg.max_iters - cfg.warmup_iters)
    coeff = 0.5 * (1.0 + math.cos(math.pi * decay_ratio))
    return cfg.min_lr + coeff * (cfg.learning_rate - cfg.min_lr)


@torch.no_grad()
def estimate_loss(model, train_ds, val_ds, cfg: TinyGPTConfig):
    """Chapter 28: Validation — average loss over eval_iters batches, no gradient tracking."""
    out = {}
    model.eval()
    for split, ds in [("train", train_ds), ("val", val_ds)]:
        losses = torch.zeros(cfg.eval_iters)
        for k in range(cfg.eval_iters):
            x, y = get_batch(ds, cfg.batch_size, cfg.device)
            _, loss = model(x, y)
            losses[k] = loss.item()
        out[split] = losses.mean().item()
    model.train()
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data/bin")
    parser.add_argument("--out_dir", type=str, default="checkpoints")
    parser.add_argument("--resume", type=str, default=None, help="path to checkpoint to resume from")
    args = parser.parse_args()

    cfg = TinyGPTConfig()
    if not torch.cuda.is_available():
        cfg.device = "cpu"
        print("⚠️  No GPU detected, falling back to CPU (training will be much slower).")

    os.makedirs(args.out_dir, exist_ok=True)

    train_ds = TokenDataset(os.path.join(args.data_dir, "train.bin"), cfg.block_size)
    val_ds = TokenDataset(os.path.join(args.data_dir, "val.bin"), cfg.block_size)

    model = TinyGPT(cfg).to(cfg.device)
    print(f"Model params: {model.num_params():,} (~{model.num_params()/1e6:.2f}M)")

    # Chapter 25: Optimizer — AdamW with weight decay only on 2D+ params (not biases/norms)
    decay_params = [p for n, p in model.named_parameters() if p.dim() >= 2]
    no_decay_params = [p for n, p in model.named_parameters() if p.dim() < 2]
    optimizer = torch.optim.AdamW(
        [
            {"params": decay_params, "weight_decay": cfg.weight_decay},
            {"params": no_decay_params, "weight_decay": 0.0},
        ],
        lr=cfg.learning_rate,
        betas=(0.9, 0.95),
    )

    start_iter = 0
    best_val_loss = float("inf")
    if args.resume:
        ckpt = torch.load(args.resume, map_location=cfg.device)
        model.load_state_dict(ckpt["model"])
        optimizer.load_state_dict(ckpt["optimizer"])
        start_iter = ckpt["iter"] + 1
        best_val_loss = ckpt.get("best_val_loss", float("inf"))
        print(f"Resumed from {args.resume} at iter {start_iter}")

    t0 = time.time()
    for it in range(start_iter, cfg.max_iters):
        lr = get_lr(it, cfg)
        for param_group in optimizer.param_groups:
            param_group["lr"] = lr

        # Chapter 24: Training Loop with gradient accumulation
        optimizer.zero_grad(set_to_none=True)
        for micro_step in range(cfg.grad_accum_steps):
            x, y = get_batch(train_ds, cfg.batch_size, cfg.device)
            _, loss = model(x, y)
            loss = loss / cfg.grad_accum_steps
            loss.backward()

        torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.grad_clip)
        optimizer.step()

        if it % cfg.eval_interval == 0 or it == cfg.max_iters - 1:
            losses = estimate_loss(model, train_ds, val_ds, cfg)
            dt = time.time() - t0
            print(
                f"iter {it:6d} | train loss {losses['train']:.4f} | "
                f"val loss {losses['val']:.4f} | lr {lr:.2e} | {dt:.1f}s"
            )

            # Chapter 27: Checkpoints — always save 'last', save 'best' only when val improves
            ckpt = {
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "iter": it,
                "best_val_loss": best_val_loss,
                "config": cfg.__dict__,
            }
            torch.save(ckpt, os.path.join(args.out_dir, "last.pt"))
            if losses["val"] < best_val_loss:
                best_val_loss = losses["val"]
                ckpt["best_val_loss"] = best_val_loss
                torch.save(ckpt, os.path.join(args.out_dir, "best.pt"))
                print(f"  ↳ new best val loss, saved best.pt")

    print("Training complete.")


if __name__ == "__main__":
    main()
