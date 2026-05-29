---
title: Software 2.0
type: concept
status: draft
created: 2026-05-28
updated: 2026-05-28
sources:
  - software-2-0-essay
  - nanogpt-readme
  - llm-c-readme
tags:
  - neural-networks
  - systems
  - ai
aliases:
  - Software Two Point Zero
related:
  - neural-networks.md
  - ../projects/llm-c.md
  - ../projects/nanogpt.md
confidence: medium
---

# Software 2.0

Software 2.0 is Karpathy's framing for neural networks as a new kind of software artifact: instead of manually written imperative logic, behavior is encoded in trained model weights. (source: `software-2-0-essay`)

## Source-Backed Claims

- The Software 2.0 essay frames neural networks as software artifacts whose behavior is encoded in trained weights. (source: `software-2-0-essay`)
- The nanoGPT README is a compact GPT-style project source that connects Software 2.0 to readable transformer training code. (source: `nanogpt-readme`)
- The llm.c README is a low-level language-model implementation source that connects Software 2.0 to systems mechanics. (source: `llm-c-readme`)

## Working Synthesis

The concept helps connect several parts of Karpathy's public work:

- [Neural Networks](neural-networks.md) are the substrate.
- [nanoGPT](../projects/nanogpt.md) shows a compact, readable version of modern transformer training.
- [llm.c](../projects/llm-c.md) moves closer to the metal, exposing the implementation mechanics of language models.

## Open Questions

- How should this page distinguish Karpathy's original Software 2.0 argument from later LLM and agent-era interpretations?
- Which passages from the original essay should anchor the summary?

## Improvement Note

<!-- improvement:what-connects-software-2-0-nanogpt-and-llm-c -->

Feedback query: `What connects Software 2.0, nanoGPT, and llm.c?`

Baseline score: `0.35`

Feedback: Missing the through-line: making neural network systems more understandable, teachable, and close to the metal.

Durable update: Add a reusable synthesis note connecting the three pages.
