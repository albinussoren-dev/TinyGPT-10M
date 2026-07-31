"""
TinyGPT-10M — Model Architecture
Covers Chapters 11-19:
  11. Embeddings
  12. Positional Encoding
  13. Self Attention
  14. Multi Head Attention
  15. Feed Forward
  16. LayerNorm
  17. Residual Connection
  18. Transformer Block
  19. GPT Architecture
"""

import math
import torch
import torch.nn as nn
from torch.nn import functional as F

from config import TinyGPTConfig


class LayerNorm(nn.Module):
    """Chapter 16: LayerNorm with optional bias (bias=False saves params, trains fine)."""

    def __init__(self, ndim, bias):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(ndim))
        self.bias = nn.Parameter(torch.zeros(ndim)) if bias else None

    def forward(self, x):
        return F.layer_norm(x, self.weight.shape, self.weight, self.bias, 1e-5)


class CausalSelfAttention(nn.Module):
    """
    Chapter 13-14: Self Attention + Multi Head Attention.
    Causal = each token can only attend to itself and previous tokens
    (this is what makes it a *language model* and not a bidirectional encoder).
    """

    def __init__(self, cfg: TinyGPTConfig):
        super().__init__()
        assert cfg.n_embd % cfg.n_head == 0, "n_embd must be divisible by n_head"
        self.n_head = cfg.n_head
        self.n_embd = cfg.n_embd
        self.head_dim = cfg.n_embd // cfg.n_head

        # combined Q, K, V projection (faster than 3 separate Linear layers)
        self.qkv_proj = nn.Linear(cfg.n_embd, 3 * cfg.n_embd, bias=cfg.bias)
        self.out_proj = nn.Linear(cfg.n_embd, cfg.n_embd, bias=cfg.bias)

        self.attn_dropout = nn.Dropout(cfg.dropout)
        self.resid_dropout = nn.Dropout(cfg.dropout)
        self.dropout = cfg.dropout

        # causal mask: lower-triangular matrix so position i can't see j > i
        self.register_buffer(
            "causal_mask",
            torch.tril(torch.ones(cfg.block_size, cfg.block_size)).view(
                1, 1, cfg.block_size, cfg.block_size
            ),
        )

    def forward(self, x):
        B, T, C = x.shape  # batch, sequence length, embedding dim

        qkv = self.qkv_proj(x)  # (B, T, 3*C)
        q, k, v = qkv.split(self.n_embd, dim=2)

        # reshape into heads: (B, n_head, T, head_dim)
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)

        # scaled dot-product attention (Chapter 13 core formula):
        # Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) V
        if hasattr(F, "scaled_dot_product_attention"):
            # uses PyTorch's fused, memory-efficient kernel (flash-attention style)
            y = F.scaled_dot_product_attention(
                q, k, v,
                attn_mask=None,
                dropout_p=self.dropout if self.training else 0.0,
                is_causal=True,
            )
        else:
            att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(self.head_dim))
            att = att.masked_fill(self.causal_mask[:, :, :T, :T] == 0, float("-inf"))
            att = F.softmax(att, dim=-1)
            att = self.attn_dropout(att)
            y = att @ v

        y = y.transpose(1, 2).contiguous().view(B, T, C)  # merge heads back
        y = self.resid_dropout(self.out_proj(y))
        return y


class FeedForward(nn.Module):
    """Chapter 15: position-wise feed-forward network (MLP), 4x expansion is the GPT standard."""

    def __init__(self, cfg: TinyGPTConfig):
        super().__init__()
        hidden = 4 * cfg.n_embd
        self.net = nn.Sequential(
            nn.Linear(cfg.n_embd, hidden, bias=cfg.bias),
            nn.GELU(),
            nn.Linear(hidden, cfg.n_embd, bias=cfg.bias),
            nn.Dropout(cfg.dropout),
        )

    def forward(self, x):
        return self.net(x)


class TransformerBlock(nn.Module):
    """
    Chapter 17-18: Residual Connection + Transformer Block.
    Pre-norm design (LayerNorm before attention/FFN, not after) — more stable training.
    """

    def __init__(self, cfg: TinyGPTConfig):
        super().__init__()
        self.ln_1 = LayerNorm(cfg.n_embd, cfg.bias)
        self.attn = CausalSelfAttention(cfg)
        self.ln_2 = LayerNorm(cfg.n_embd, cfg.bias)
        self.ffwd = FeedForward(cfg)

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))   # residual around attention
        x = x + self.ffwd(self.ln_2(x))   # residual around feed-forward
        return x


class TinyGPT(nn.Module):
    """Chapter 19: full GPT architecture — the model you'll train, quantize, and ship to Android."""

    def __init__(self, cfg: TinyGPTConfig):
        super().__init__()
        self.cfg = cfg

        self.token_emb = nn.Embedding(cfg.vocab_size, cfg.n_embd)      # Chapter 11
        self.pos_emb = nn.Embedding(cfg.block_size, cfg.n_embd)        # Chapter 12
        self.drop = nn.Dropout(cfg.dropout)
        self.blocks = nn.ModuleList([TransformerBlock(cfg) for _ in range(cfg.n_layer)])
        self.ln_f = LayerNorm(cfg.n_embd, cfg.bias)
        self.lm_head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)

        # weight tying: input embedding and output projection share weights
        # (standard GPT-2 trick, saves ~vocab_size*n_embd params)
        self.token_emb.weight = self.lm_head.weight

        self.apply(self._init_weights)
        # scaled init for residual projections (GPT-2 paper trick, helps deep nets converge)
        for pn, p in self.named_parameters():
            if pn.endswith("out_proj.weight") or pn.endswith("net.2.weight"):
                nn.init.normal_(p, mean=0.0, std=0.02 / math.sqrt(2 * cfg.n_layer))

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        assert T <= self.cfg.block_size, f"sequence length {T} > block_size {self.cfg.block_size}"

        pos = torch.arange(0, T, dtype=torch.long, device=idx.device)
        x = self.token_emb(idx) + self.pos_emb(pos)   # Chapter 20: token + position -> input repr
        x = self.drop(x)

        for block in self.blocks:
            x = block(x)
        x = self.ln_f(x)

        if targets is not None:
            logits = self.lm_head(x)
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)), targets.view(-1), ignore_index=-1
            )
        else:
            # inference: only compute logits for the last position (saves compute)
            logits = self.lm_head(x[:, [-1], :])
            loss = None

        return logits, loss

    def num_params(self):
        n = sum(p.numel() for p in self.parameters())
        n -= self.pos_emb.weight.numel()  # conventionally excluded from "model size" headline number
        return n

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None, top_p=None):
        """Chapter 29-30: autoregressive generation with temperature / top-k / top-p sampling."""
        self.eval()
        for _ in range(max_new_tokens):
            idx_cond = idx if idx.size(1) <= self.cfg.block_size else idx[:, -self.cfg.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / max(temperature, 1e-5)

            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float("-inf")

            if top_p is not None:
                sorted_logits, sorted_idx = torch.sort(logits, descending=True)
                probs = F.softmax(sorted_logits, dim=-1)
                cum_probs = torch.cumsum(probs, dim=-1)
                sorted_mask = cum_probs > top_p
                sorted_mask[:, 1:] = sorted_mask[:, :-1].clone()
                sorted_mask[:, 0] = False
                mask = sorted_mask.scatter(1, sorted_idx, sorted_mask)
                logits[mask] = float("-inf")

            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx


if __name__ == "__main__":
    cfg = TinyGPTConfig()
    model = TinyGPT(cfg)
    print(f"TinyGPT params: {model.num_params():,} (~{model.num_params()/1e6:.2f}M)")
