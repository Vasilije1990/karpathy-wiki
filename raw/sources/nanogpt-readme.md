# Source: nanoGPT README

source_id: nanogpt-readme
title: nanoGPT README
url: https://raw.githubusercontent.com/karpathy/nanoGPT/master/README.md
kind: github-readme
status: captured-as-excerpt
captured: 2026-05-28

## Extracted Headings

- nanoGPT
- install
- quick start
- reproducing GPT-2
- Run on the first (master) node with example IP 123.456.123.456:
- Run on the worker node:
- baselines
- finetuning
- sampling / inference
- efficiency notes
- todos
- troubleshooting

## Excerpt

---

**Update Nov 2025** nanoGPT has a new and improved cousin called [nanochat](https://github.com/karpathy/nanochat). It is very likely you meant to use/find nanochat instead. nanoGPT (this repo) is now very old and deprecated but I will leave it up for posterity.

---

The simplest, fastest repository for training/finetuning medium-sized GPTs. It is a rewrite of [minGPT](https://github.com/karpathy/minGPT) that prioritizes teeth over education. Still under active development, but currently the file `train.py` reproduces GPT-2 (124M) on OpenWebText, running on a single 8XA100 40GB node in about 4 days of training. The code itself is plain and readable: `train.py` is a ~300-line boilerplate training loop and `model.py` a ~300-line GPT model definition, which can optionally load the GPT-2 weights from OpenAI. That's it.

Because the code is so simple, it is very easy to hack to your needs, train new models from scratch, or finetune pretrained checkpoints (e.g. biggest one currently available as a starting point would be the GPT-2 1.3B model from OpenAI).

```

pip install torch numpy transformers datasets tiktoken wandb tqdm

```

Dependencies:

- [pytorch](https://pytorch.org) <3

- [numpy](https://numpy.org/install/) <3

- `transformers` for huggingface transformers <3 (to load GPT-2 checkpoints)

## Capture Policy

This source record stores metadata, headings, and excerpts for wiki synthesis. It does not attempt to mirror the full upstream page.
