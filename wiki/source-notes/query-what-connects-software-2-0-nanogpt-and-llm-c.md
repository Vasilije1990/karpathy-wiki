---
title: Query Synthesis - What connects Software 2.0, nanoGPT, and llm.c?
type: source-note
status: reviewed
created: 2026-05-28
updated: 2026-05-28
sources:
  - llm-c-readme
  - mingpt-readme
  - nanogpt-readme
  - software-2-0-essay
tags:
  - query
  - synthesis
aliases:
  - What connects Software 2.0, nanoGPT, and llm.c?
related:
  - ../concepts/software-2-0.md
  - ../source-notes/software-2-0-essay.md
  - ../projects/llm-c.md
  - ../projects/nanogpt.md
  - ../source-notes/llm-c-readme.md
confidence: medium
---

<!-- auto-filed-query-answer: true -->

# Answer: What connects Software 2.0, nanoGPT, and llm.c?

## Direct Answer

The current wiki connects Software 2.0, nanoGPT, and llm.c through an educational systems thread: Software 2.0 frames trained neural networks as software artifacts (sources: `llm-c-readme`, `nanogpt-readme`, `software-2-0-essay`). nanoGPT makes GPT-style training small enough to inspect (sources: `llm-c-readme`, `mingpt-readme`, `nanogpt-readme`). llm.c moves the same learning surface closer to low-level implementation (sources: `llm-c-readme`, `nanogpt-readme`, `software-2-0-essay`). Synthesis: Karpathy's public work often turns complex neural-network systems into readable artifacts that teach the mechanism. Cognee recall reinforces this by surfacing remembered source context around the same project and concept cluster.

## Evidence

- `concepts/software-2-0.md` (score 33, sources: software-2-0-essay, nanogpt-readme, llm-c-readme): Software 2.0 is Karpathy's framing for neural networks as a new kind of software artifact: instead of manually written imperative logic, behavior is encoded in trained model weights. (source: `software-2-0-essay`)
- `source-notes/software-2-0-essay.md` (score 30, sources: software-2-0-essay): - Source ID: `software-2-0-essay`
- `projects/llm-c.md` (score 15, sources: llm-c-readme, nanogpt-readme, software-2-0-essay): llm.c is a public implementation project that makes language-model mechanics visible at a lower systems level. In this wiki, it is a bridge between [Software 2.0](../concepts/software-2-0.md), educational implementations, and systems-level understanding. (source: `llm-c-readme`)
- `projects/nanogpt.md` (score 15, sources: nanogpt-readme, mingpt-readme, llm-c-readme): nanoGPT is a compact public implementation project associated with GPT-style model training. In this wiki, it is treated as both a project page and an educational bridge between transformer concepts and runnable code. (source: `nanogpt-readme`)
- `source-notes/llm-c-readme.md` (score 11, sources: llm-c-readme): - URL: https://raw.githubusercontent.com/karpathy/llm.c/master/README.md
- `source-notes/nanogpt-readme.md` (score 10, sources: nanogpt-readme): - Source ID: `nanogpt-readme`

## Cognee Recall

- "kind='graph_completion' search_type='GRAPH_COMPLETION_CONTEXT_EXTENSION' text='They’re all part of Andrej Karpathy’s work — “Software 2.0” is his essay on neural‑net–driven software, nanoGPT is his compact GPT implementation, and llm.c is a C/CUDA project (a slight tweak/descendant of nanoGPT) by him.' score=None dataset_id='72f25976-2379-5029-857e-2b5082792fd4' dataset_name='karpathy-wiki' metadata={} raw={'value': 'They’re all part of Andrej Karpathy’s work — “Software 2.0” is his essay on neural‑net–driven software, nanoGPT is his compact GPT implementation, and llm.c is a C/CUDA project (a slight tweak/descendant of nanoGPT) by him.'} structured=None source='graph'" (sources: source id not found in memory)

## Source IDs

- `llm-c-readme`
- `mingpt-readme`
- `nanogpt-readme`
- `software-2-0-essay`

## Filing Recommendation

When this answer is run with `--file-answer` or through the website API, it is stored as a durable query synthesis page. Stable claims should still be promoted into the most relevant concept or project page during maintenance.
