---
title: LLM Wiki
type: concept
status: draft
created: 2026-05-28
updated: 2026-05-28
sources:
  - llm-wiki-gist
  - karpathy-wiki-operating-schema
tags:
  - knowledge-management
  - agents
  - wiki
aliases:
  - Karpathy LLM Wiki
  - Persistent LLM Wiki
related:
  - ../index.md
  - ../source-notes/llm-wiki-gist.md
  - agents.md
confidence: high
---

# LLM Wiki

An LLM Wiki is a persistent markdown knowledge base maintained by an agent. Raw sources are immutable, while the LLM-owned wiki layer is updated as new material arrives and as queries reveal useful synthesis. (source: `llm-wiki-gist`)

## Source-Backed Claims

- The LLM Wiki gist source describes a persistent markdown wiki maintained by an agent. (source: `llm-wiki-gist`)
- The LLM Wiki gist source separates raw source material from generated wiki pages. (source: `llm-wiki-gist`)
- The LLM Wiki gist source motivates an index, log, schema, and cross-linked markdown pages. (source: `llm-wiki-gist`)

## Core Pattern

- Raw sources are kept separately from generated wiki pages.
- The wiki is a directory of markdown files with summaries, entity pages, concept pages, and cross-references.
- A schema file tells the agent how to ingest, query, lint, and improve the wiki.
- `index.md` helps navigation by topic.
- `log.md` records operations chronologically.

## Why It Matters Here

This Karpathy wiki applies the pattern to Karpathy's own public work. Cognee provides durable structured memory, the filesystem cache provides session memory, and markdown remains the human-readable artifact. (source: `karpathy-wiki-operating-schema`)

## Related Pages

- [Agents](agents.md)
- [Source Note: LLM Wiki Gist](../source-notes/llm-wiki-gist.md)
