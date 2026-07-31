"""
TinyGPT-10M — Text Generation
Covers Chapters 29-30: Text Generation, Sampling

Usage:
    python generate.py --checkpoint checkpoints/best.pt --tokenizer tokenizer/tinygpt_tokenizer.model \
        --prompt "Once upon a time" --max_new_tokens 100 --temperature 0.8 --top_k 50
"""

import argparse
import torch

from config import TinyGPTConfig
from model import TinyGPT
from tokenizer.train_tokenizer import TinyTokenizer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=str, required=True)
    parser.add_argument("--tokenizer", type=str, required=True)
    parser.add_argument("--prompt", type=str, default="")
    parser.add_argument("--max_new_tokens", type=int, default=100)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top_k", type=int, default=50)
    parser.add_argument("--top_p", type=float, default=None)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    ckpt = torch.load(args.checkpoint, map_location=device)
    cfg = TinyGPTConfig(**{k: v for k, v in ckpt["config"].items() if k in TinyGPTConfig.__dataclass_fields__})
    cfg.device = device

    model = TinyGPT(cfg).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()

    tok = TinyTokenizer(args.tokenizer)

    ids = tok.encode(args.prompt, add_bos=True)
    idx = torch.tensor([ids], dtype=torch.long, device=device)

    out = model.generate(
        idx,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
    )

    text = tok.decode(out[0].tolist())
    print("\n--- Generated ---\n")
    print(text)


if __name__ == "__main__":
    main()
