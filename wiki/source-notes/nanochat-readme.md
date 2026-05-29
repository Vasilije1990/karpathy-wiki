---
title: Source Note - nanochat README
type: source-note
status: draft
created: 2026-05-28
updated: 2026-05-28
sources:
  - nanochat-readme
tags:
  - source-note
  - project
  - llm
  - education
aliases:
  - nanochat README
related:
  - ../projects/nanogpt.md
  - ../concepts/agents.md
confidence: medium
---

# Source Note - nanochat README

## Source

- Source ID: `nanochat-readme`
- URL: https://raw.githubusercontent.com/karpathy/nanochat/master/README.md
- Kind: github-readme

## Extracted Headings

- nanochat
- Time-to-GPT-2 Leaderboard
- Getting started
- Setup
- Reproduce and talk to GPT-2
- Research
- Running on CPU / MPS
- Precision / dtype
- Guides
- File structure

## Candidate Observations

- | # | time | val_bpb | CORE | Description | Date | Commit | Contributors |
- |---|-------------|---------|------|-------------|------|--------|--------------|
- | 0 | 168 hours | - | 0.2565 | Original OpenAI GPT-2 checkpoint | 2019 | - | OpenAI |
- | 1 | 3.04 | 0.74833 | 0.2585 | d24 baseline, slightly overtrained | Jan 29 2026 | 348fbb3 | @karpathy |
- | 2 | 2.91 | 0.74504 | 0.2578 | d26 slightly undertrained **+fp8** | Feb 2 2026 | a67eba3 | @karpathy |
- | 3 | 2.76 | 0.74645 | 0.2602 | bump total batch size to 1M tokens | Feb 5 2026 | 2c062aa | @karpathy |

## Useful Links

- [nanochat logo](dev/nanochat.png)
- [scaling laws](dev/scaling_laws_jan26.png)
- [DeepWiki](https://deepwiki.com/karpathy/nanochat)
- [Discussions tab](https://github.com/karpathy/nanochat/discussions)
- [#nanochat](https://discord.com/channels/1020383067459821711/1427295580895314031)
- [runs/speedrun.sh](runs/speedrun.sh)
- [round 1](https://x.com/karpathy/status/2031135152349524125)
- [dev/LEADERBOARD.md](https://github.com/karpathy/nanochat/blob/master/dev/LEADERBOARD.md)

## Follow-Up

- Decide which topic or project pages should absorb this source.
- Add source-backed claims to related pages after reviewing the upstream source.
