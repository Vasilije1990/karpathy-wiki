# Andrej Karpathy Wiki Operating Schema

This project follows the LLM Wiki pattern: raw sources are immutable, the wiki is a persistent markdown artifact, and the agent maintains page structure, links, citations, and logs.

## Layers

- `raw/sources/`: source records, metadata, excerpts, and local notes. Treat these as source of truth. Do not rewrite their factual content during wiki maintenance.
- `wiki/`: human-readable wiki pages. The agent may create and update these pages.
- `skills/`: reusable instructions for Cognee-backed workflows.
- Cognee: durable memory for entities, concepts, claims, summaries, relationships, contradictions, and feedback.
- Cognee filesystem session cache: fast local per-session memory for observations, draft claims, query traces, and feedback before distillation. Use `CACHING=true` and `CACHE_BACKEND=fs`.

## Required Page Frontmatter

Every wiki page must start with:

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

## Citation Rules

- Any concrete claim about Karpathy's biography, projects, employers, publications, talks, or public statements needs a source entry.
- Synthesis is allowed, but label it as synthesis and connect it to source-backed observations.
- Do not copy large copyrighted transcripts or articles into the wiki. Prefer metadata, short excerpts, and links to canonical sources.
- If a source cannot be fetched without login or licensing friction, create a source placeholder and mark the status.

## Ingest Workflow

1. Add source metadata or source text under `raw/sources/`.
2. Extract entities, concepts, projects, claims, dates, and open questions.
3. Write run-local observations to Cognee session memory using the active `session_id`.
4. Promote durable facts, summaries, and relationships into Cognee.
5. Update or create wiki pages.
6. Update `wiki/index.md` and append to `wiki/log.md`.

## Query Workflow

1. Read `wiki/index.md` first.
2. Search relevant markdown pages and source notes.
3. Recall related durable memory from Cognee when available.
4. Answer with citations to source notes or source IDs.
5. If the answer creates reusable synthesis, file it as a page update or source note.

## Lint Workflow

Run lint periodically and before publishing:

- broken relative markdown links
- missing frontmatter
- missing source IDs
- orphan pages
- duplicate titles or aliases
- TODO markers that should become open questions
- stale or contradictory claims

## Self-Improvement Workflow

When feedback says an answer was weak:

1. Record the query, answer, feedback, and score.
2. Identify missing pages, missing links, stale summaries, or weak skills.
3. Apply focused markdown changes.
4. Store an improvement record in Cognee when available.
5. Re-run the query and compare the answer.
