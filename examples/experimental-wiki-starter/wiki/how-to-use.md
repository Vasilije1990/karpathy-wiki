---
title: How To Use This Wiki
type: overview
status: seed
created: 2026-05-31
updated: 2026-05-31
sources:
  - seed
tags:
  - guide
  - workflow
aliases:
  - User Guide
related:
  - index.md
  - source-notes/seed.md
confidence: medium
---

# How To Use This Wiki

Use `raw/sources/` for source records, `wiki/` for readable pages, and Cognee for optional durable memory.

## Add Sources

```bash
uv run scripts/ingest.py raw/sources/seed.md --session experimental-wiki-ingest --dataset experimental-wiki
```

## Ask Questions

```bash
uv run scripts/query.py "What is this wiki about?" --session experimental-wiki-query --dataset experimental-wiki --file-answer --reviewed
```

## Check Health

```bash
uv run scripts/lint_wiki.py
uv run scripts/lint_wiki.py --strict-citations --semantic
```
