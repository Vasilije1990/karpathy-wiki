---
title: Source Note - nanoGPT README
type: source-note
status: draft
created: 2026-05-28
updated: 2026-05-28
sources:
  - nanogpt-readme
tags:
  - source-note
  - project
  - transformers
  - education
aliases:
  - nanoGPT README
related:
  - ../projects/nanogpt.md
  - ../concepts/education.md
confidence: medium
---

# Source Note - nanoGPT README

## Source

- Source ID: `nanogpt-readme`
- URL: https://raw.githubusercontent.com/karpathy/nanoGPT/master/README.md
- Kind: github-readme

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

## Candidate Observations

- Because the code is so simple, it is very easy to hack to your needs, train new models from scratch, or finetune pretrained checkpoints (e.g. biggest one currently available as a starting point would be the GPT-2 1.3B model from OpenAI).
- pip install torch numpy transformers datasets tiktoken wandb tqdm
- - `transformers` for huggingface transformers <3 (to load GPT-2 checkpoints)
- - `datasets` for huggingface datasets <3 (if you want to download + preprocess OpenWebText)
- This creates a `train.bin` and `val.bin` in that data directory. Now it is time to train your GPT. The size of it very much depends on the computational resources of your system:
- **I have a GPU**. Great, we can quickly train a baby GPT with the settings provided in the [config/train_shakespeare_char.py](config/train_shakespeare_char.py) config file:

## Useful Links

- [nanoGPT](assets/nanogpt.jpg)
- [nanochat](https://github.com/karpathy/nanochat)
- [minGPT](https://github.com/karpathy/minGPT)
- [repro124m](assets/gpt2_124M_loss.png)
- [pytorch](https://pytorch.org)
- [numpy](https://numpy.org/install/)
- [config/train_shakespeare_char.py](config/train_shakespeare_char.py)
- [select it here](https://pytorch.org/get-started/locally/)

## Follow-Up

- Decide which topic or project pages should absorb this source.
- Add source-backed claims to related pages after reviewing the upstream source.
