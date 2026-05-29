# Source: Karpathy Wiki Operating Schema

source_id: karpathy-wiki-operating-schema
title: Karpathy Wiki Operating Schema
url: AGENTS.md
kind: local-operating-schema
status: captured-as-local-schema
captured: 2026-05-28

## Extracted Claims

- Raw sources live under `raw/sources/` and are treated as source of truth.
- Human-readable wiki pages live under `wiki/`.
- Cognee is durable memory for entities, concepts, claims, summaries, relationships, contradictions, and feedback.
- Cognee filesystem session cache stores fast local per-session observations, draft claims, query traces, and feedback before distillation.
- This project uses `CACHING=true` and `CACHE_BACKEND=fs`.
- Query answers that create reusable synthesis should be filed as page updates or source notes.

## Capture Policy

This local source record captures the project operating schema relevant to Cognee-backed wiki maintenance. It is not a public Karpathy source.
