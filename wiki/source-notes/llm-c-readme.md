---
title: Source Note - llm.c README
type: source-note
status: draft
created: 2026-05-28
updated: 2026-05-28
sources:
  - llm-c-readme
tags:
  - source-note
  - project
  - systems
  - llm
aliases:
  - llm.c README
related:
  - ../projects/llm-c.md
  - ../concepts/software-2-0.md
confidence: medium
---

# Source Note - llm.c README

## Source

- Source ID: `llm-c-readme`
- URL: https://raw.githubusercontent.com/karpathy/llm.c/master/README.md
- Kind: github-readme

## Extracted Headings

- llm.c
- quick start
- quick start (1 GPU, fp32 only)
- quick start (CPU)
- datasets
- test
- fp32 test (cudnn not supported)
- mixed precision cudnn test
- tutorial
- multi-GPU training

## Candidate Observations

- debugging tip: when you run the `make` command to build the binary, modify it by replacing `-O3` with `-g` so you can step through the code in your favorite IDE (e.g. vscode).
- If you'd prefer to avoid running the starter pack script, then as mentioned in the previous section you can reproduce the exact same .bin files and artifacts by running `python dev/data/tinyshakespeare.py` and then `python train_gpt2.py`.

## Useful Links

- [GPT-2](https://github.com/openai/gpt-2)
- [GPT-3](https://arxiv.org/abs/2005.14165)
- [train_gpt2.py](train_gpt2.py)
- [nanoGPT](https://github.com/karpathy/nanoGPT)
- [train_gpt2.cu](train_gpt2.cu)
- [train_gpt2.c](train_gpt2.c)
- [Discussions](https://github.com/karpathy/llm.c/discussions)
- [Zero to Hero](https://discord.gg/3zy8kqD9Cp)

## Follow-Up

- Decide which topic or project pages should absorb this source.
- Add source-backed claims to related pages after reviewing the upstream source.
