---
title: Source Note - minGPT README
type: source-note
status: draft
created: 2026-05-28
updated: 2026-05-28
sources:
  - mingpt-readme
tags:
  - source-note
  - project
  - transformers
  - education
aliases:
  - minGPT README
related:
  - ../projects/mingpt.md
  - ../concepts/education.md
confidence: medium
---

# Source Note - minGPT README

## Source

- Source ID: `mingpt-readme`
- URL: https://raw.githubusercontent.com/karpathy/minGPT/master/README.md
- Kind: github-readme

## Extracted Headings

- minGPT
- Library Installation
- Usage
- your subclass of torch.utils.data.Dataset that emits example
- torch LongTensor of lengths up to 1024, with integers from [0,50257)
- Unit tests
- todos
- References
- Improving Language Understanding by Generative Pre-Training (GPT-1)
- Language Models are Unsupervised Multitask Learners (GPT-2)

## Candidate Observations

- - `projects/adder` trains a GPT from scratch to add numbers (inspired by the addition section in the GPT-3 paper)
- - `projects/chargpt` trains a GPT to be a character-level language model on some input text file
- - `demo.ipynb` shows a minimal usage of the `GPT` and `Trainer` in a notebook format on a simple sorting example
- - `generate.ipynb` shows how one can load a pretrained GPT2 and generate text given some prompt
- Here's how you'd instantiate a GPT-2 (124M param version):
- model_config.vocab_size = 50257 # openai's model vocabulary

## Useful Links

- [mingpt](mingpt.jpg)
- [GPT](https://github.com/openai/gpt-2)
- [mingpt/model.py](mingpt/model.py)
- [Transformer](https://arxiv.org/abs/1706.03762)
- [nanoGPT](https://github.com/karpathy/nanoGPT)
- [mingpt/model.py](mingpt/model.py)
- [mingpt/bpe.py](mingpt/bpe.py)
- [mingpt/trainer.py](mingpt/trainer.py)

## Follow-Up

- Decide which topic or project pages should absorb this source.
- Add source-backed claims to related pages after reviewing the upstream source.
