# Source: Source: LLM Wiki Gist

source_id: llm-wiki-gist
title: Source: LLM Wiki Gist
url: 
status: captured
captured: 2026-05-28

## Content

# Source: LLM Wiki Gist

source_id: llm-wiki-gist
title: LLM Wiki
author: Andrej Karpathy
url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
status: captured-as-summary
captured: 2026-05-28

## Summary

Karpathy describes an LLM-maintained personal knowledge base where raw sources remain immutable, the LLM incrementally maintains a directory of markdown wiki pages, and a schema file tells the agent how to ingest, query, and lint the wiki.

The core distinction from RAG is persistence. Instead of re-discovering knowledge from source chunks at query time, the agent compiles source material into an evolving wiki that keeps summaries, entity pages, concept pages, cross-references, contradictions, and logs current.

## Key Ideas

- The wiki is a persistent, compounding artifact.
- Raw sources, generated wiki pages, and schema/instructions are separate layers.
- Ingest updates multiple pages, not just an embedding index.
- Query answers can become durable pages when they contain reusable synthesis.
- Linting checks contradictions, stale claims, orphans, missing links, and source gaps.
- `index.md` is content-oriented navigation.
- `log.md` is chronological operational memory.

## Notes

This file intentionally stores a summary and metadata rather than a full copy of the gist.
