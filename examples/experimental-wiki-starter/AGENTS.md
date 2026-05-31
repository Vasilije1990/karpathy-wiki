# Experimental LLM Wiki Operating Schema

This project follows the LLM Wiki pattern: raw sources are immutable, the wiki is a persistent markdown artifact, and the agent maintains page structure, links, citations, and logs.

## Layers

- `raw/sources/`: source records, metadata, excerpts, and local notes.
- `wiki/`: human-readable wiki pages.
- `skills/`: optional reusable instructions for wiki workflows.
- Cognee: optional durable memory for entities, concepts, claims, summaries, relationships, contradictions, and feedback.
- Cognee filesystem session cache: fast local per-session memory. Use `CACHING=true` and `CACHE_BACKEND=fs`.

## Required Page Frontmatter

```yaml
---
title: Page Title
type: overview | person | concept | project | source-note | timeline | log
status: seed | draft | reviewed
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources:
  - source-id
tags:
  - tag
aliases:
  - Alternate Name
related:
  - relative/path.md
confidence: low | medium | high
---
```

## Core Loop

1. Add source metadata or source text under `raw/sources/`.
2. Extract entities, concepts, claims, dates, and open questions.
3. Write run-local observations to session memory with the active `session_id`.
4. Promote durable facts, summaries, and relationships into Cognee when provider access is configured.
5. Update or create wiki pages.
6. Update `wiki/index.md` and append to `wiki/log.md`.
