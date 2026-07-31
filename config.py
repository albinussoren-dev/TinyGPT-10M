"""
TinyGPT-10M — Model Configuration
Chapter 21: Model Config

~10M parameters ka target rakhते हुए ye config choose ki gayi hai.
Formula (approx, ignoring embeddings tie-in): 
params ≈ 12 * n_layer * n_embd^2  (transformer blocks)
       + vocab_size * n_embd      (token embedding, tied with output head)
"""

from dataclasses import dataclass


@dataclass
class TinyGPTConfig:
    # --- Vocabulary / Tokenizer ---
    vocab_size: int = 8000        # SentencePiece BPE vocab size (Chapter 9-10)

    # --- Architecture (Chapter 19: GPT Architecture) ---
    n_layer: int = 6              # number of transformer blocks
    n_head: int = 6               # number of attention heads
    n_embd: int = 288             # embedding dimension (must be divisible by n_head)
    block_size: int = 256         # max context length (sequence length)

    # --- Regularization ---
    dropout: float = 0.1
    bias: bool = False            # LLaMA-style: no bias in Linear/LayerNorm (fewer params, trains fine)

    # --- Training (Chapter 24-26) ---
    batch_size: int = 64
    grad_accum_steps: int = 4     # effective batch = batch_size * grad_accum_steps
    max_iters: int = 20000
    eval_interval: int = 500
    eval_iters: int = 100
    learning_rate: float = 3e-4
    min_lr: float = 3e-5
    warmup_iters: int = 500
    weight_decay: float = 0.1
    grad_clip: float = 1.0

    # --- Device ---
    device: str = "cuda"          # change to "cpu" or "mps" if no GPU

    def estimate_params(self) -> int:
        """Rough parameter count estimate."""
        emb = self.vocab_size * self.n_embd
        block = 12 * self.n_layer * (self.n_embd ** 2)
        return emb + block


if __name__ == "__main__":
    cfg = TinyGPTConfig()
    n = cfg.estimate_params()
    print(f"Estimated parameters: {n:,} (~{n/1e6:.1f}M)")
