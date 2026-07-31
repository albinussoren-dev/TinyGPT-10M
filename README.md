# TinyGPT-10M

Ek chhota (~8-10M parameter) GPT model, from scratch, jise tum train karke Android pe
offline chala sakte ho. Ye Phase 1-4 (Chapters 1-30) ka working code hai.

## Kyun ye environment mein run nahi kar sakte

Ye code Claude ke sandboxed container mein likha gaya hai jiske paas internet/GPU access
nahi hai (torch install nahi ho sakta). Isliye ye code tumhe apne machine ya **Google Colab
(free GPU)** pe chalana hoga.

## Setup (Colab ya local machine pe)

```bash
pip install -r requirements.txt
```

## Step 1 — Corpus taiyar karo

Ek `.txt` file chahiye (jitna bada utna better model). General Hindi+English text ke liye
`build_corpus.py` use karo — Wikipedia se streaming mode mein articles fetch karta hai
(internet chahiye, poora dump download nahi hota):

```bash
python build_corpus.py --hi_articles 3000 --en_articles 3000 --out data/corpus.txt
```

Ye ~3000 Hindi + 3000 English articles fetch karega, roughly 15-25M characters ka corpus
banega (chhote 10M model ke liye theek-thaak size). Zyada articles chahiye ho to
`--hi_articles` / `--en_articles` badha do — bas time zyada lagega.

## Step 2 — Tokenizer train karo (Chapter 6-10)

```bash
python tokenizer/train_tokenizer.py --input data/corpus.txt --vocab_size 8000
```

Isse `tokenizer/tinygpt_tokenizer.model` aur `.vocab` banega.

## Step 3 — Dataset binary banao (Chapter 22-23)

```bash
python data/dataset_builder.py --text data/corpus.txt \
    --tokenizer_model tokenizer/tinygpt_tokenizer.model --out_dir data/bin
```

## Step 4 — Training shuru karo (Chapter 24-28)

```bash
python train.py --data_dir data/bin --out_dir checkpoints
```

- GPU pe (Colab T4 free tier) ~8-10M param model ko 20k iterations mein train karne mein
  roughly 30-60 minutes lagenge (corpus size pe depend karta hai).
- Checkpoints `checkpoints/last.pt` aur `checkpoints/best.pt` mein save honge.
- Resume karne ke liye: `--resume checkpoints/last.pt`

## Step 5 — Text generate karo (Chapter 29-30)

```bash
python generate.py --checkpoint checkpoints/best.pt \
    --tokenizer tokenizer/tinygpt_tokenizer.model \
    --prompt "Namaste, mera naam" --max_new_tokens 100 --temperature 0.8 --top_k 50
```

## Model size tweak karna ho

`config.py` mein `n_layer`, `n_head`, `n_embd`, `vocab_size` change karo. File ke bottom
mein `python config.py` chalao to dekho estimated param count kitna aata hai.

---

## Ab tak kya bana (Phase 1-4, Chapters 1-30)

- ✅ `model.py` — GPT architecture (embeddings, positional encoding, multi-head causal
  self-attention, feed-forward, layernorm, residual connections, transformer blocks)
- ✅ `tokenizer/train_tokenizer.py` — SentencePiece BPE tokenizer trainer
- ✅ `data/dataset_builder.py` — corpus → binary token file → PyTorch Dataset
- ✅ `train.py` — full training loop: AdamW optimizer, cosine LR schedule with warmup,
  gradient accumulation, gradient clipping, validation, checkpointing (last + best)
- ✅ `generate.py` — autoregressive generation with temperature / top-k / top-p sampling
- ✅ `config.py` — single source of truth for model + training hyperparameters

## Aage kya (Phase 5-7, Chapters 31-50)

Ye abhi nahi bana — jab model train ho jaye tab ye order follow karna:

1. **Chapter 31-36 (Optimization)**: trained model ko INT8/INT4 quantize karna, fir
   ONNX ya `llama.cpp`/ExecuTorch format mein export karna — mobile pe chalane ke liye
   zaroori step hai, kyunki raw PyTorch checkpoint Android pe directly nahi chalta.
2. **Chapter 37-44 (Android)**: Kotlin + Jetpack Compose app, quantized model load
   karna, wahi tokenizer (`.model` file) Android mein bundle karna, streaming output.
3. **Chapter 45-50 (Advanced)**: LoRA fine-tuning, RAG, voice I/O, APK build, Play Store.

Jab training complete ho jaye (ya agar corpus taiyar karne mein help chahiye), bata dena —
agla step (quantization + Android integration) bhi isi tarah bana denge.
