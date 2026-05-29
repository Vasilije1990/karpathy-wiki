---
title: Source Note - Karpathy Wiki Operating Schema
type: source-note
status: reviewed
created: 2026-05-28
updated: 2026-05-28
sources:
  - karpathy-wiki-operating-schema
tags:
  - source-note
  - workflow
  - cognee
aliases:
  - Karpathy Wiki Operating Schema
related:
  - ../concepts/agents.md
  - ../concepts/llm-wiki.md
  - ../how-to-use.md
confidence: high
---

# Source Note - Karpathy Wiki Operating Schema

## Source

- Source ID: `karpathy-wiki-operating-schema`
- URL: AGENTS.md
- Kind: local-operating-schema

## Candidate Observations

- Cognee is the durable memory layer for entities, concepts, claims, summaries, relationships, contradictions, and feedback.
- Cognee filesystem session cache stores run-local observations, draft claims, query traces, and feedback before distillation.
- The required local session settings are `CACHING=true` and `CACHE_BACKEND=fs`.
- Query answers that create reusable synthesis should become page updates or source notes.

## Follow-Up

- Keep implementation docs aligned with this operating schema when scripts or website behavior change.
