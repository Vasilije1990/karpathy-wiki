---
title: How To Use This Wiki
type: overview
status: seed
created: 2026-05-28
updated: 2026-05-31
sources:
  - llm-wiki-gist
  - public-karpathy-corpus
  - cognee-resources
tags:
  - guide
  - workflow
  - usage
aliases:
  - User Guide
  - Using The Wiki
related:
  - index.md
  - generate-your-own-wiki.md
  - concepts/llm-wiki.md
  - source-notes/public-corpus-map.md
  - source-notes/cognee-resources.md
  - log.md
confidence: high
---

# How To Use This Wiki

This wiki is meant to be used as a living map of Andrej Karpathy's public work: projects, essays, courses, concepts, source notes, and synthesis across them.

## Browse

- Start at [Andrej Karpathy Wiki](index.md) for the current thesis and topic hubs.
- Open project pages such as [nanoGPT](projects/nanogpt.md), [minGPT](projects/mingpt.md), [llm.c](projects/llm-c.md), and [CS231n](projects/cs231n.md).
- Open concept pages such as [Software 2.0](concepts/software-2-0.md), [Education](concepts/education.md), [Neural Networks](concepts/neural-networks.md), and [LLM Wiki](concepts/llm-wiki.md).
- Follow the Related and Backlinks sections to move between connected ideas.
- Use the Graph panel to inspect the exported Cognee graph and jump through pages connected by Cognee entities, wiki links, shared source IDs, and shared tags.
- Use source-note pages when you need to inspect what a wiki claim is based on.

## Search

Use the search field in the sidebar for topics, projects, source IDs, or themes:

- `software`
- `transformers`
- `education`
- `agents`
- `source-note`

The search scans page titles, tags, source IDs, aliases, and page content.

## Ask Questions

In the website, open the `Ask Cognee` tab on any page. The panel calls the local wiki API, asks Cognee for recall, searches markdown evidence, and files the answer as a reviewed query synthesis page under `wiki/source-notes/`.

Run the API server beside the Vite dev server:

```bash
npm run api
```

For a local operator workflow, ask the wiki from the terminal:

```bash
python3 scripts/query.py "What connects Software 2.0, nanoGPT, and llm.c?" --session karpathy-wiki-v1 --cognee --file-answer --reviewed
```

Use `--cognee` when provider access is configured and you want Cognee graph recall. Use `--file-answer --reviewed` when the answer should become a durable reviewed source note automatically. Without `--cognee`, the query uses the markdown wiki and filesystem-backed session events only.

## Add Sources

Ingest one source:

```bash
python3 scripts/ingest.py raw/sources/llm-wiki.md --session karpathy-wiki-v1 --graph
```

Ingest the curated public corpus:

```bash
python3 scripts/ingest_public_corpus.py --session karpathy-wiki-v1 --graph
```

Use `--graph` when you want compact source summaries promoted into Cognee durable memory. Omit it when you only want local source records and source notes.

## Generate A Fresh Wiki

Use the project generator when you want a reusable experimental wiki with the same engine and a clean seed corpus:

```bash
python3 scripts/create_wiki_project.py ../my-experimental-wiki --title "My Experimental Wiki" --topic "the domain I want to study"
```

See [Generate Your Own Wiki](generate-your-own-wiki.md) for the full workflow, including the content-only starter at `examples/experimental-wiki-starter/`.

## Cognee Links

- [Cognee website](https://www.cognee.ai/)
- [Cognee documentation](https://docs.cognee.ai/)
- [Cognee GitHub](https://github.com/topoteretes/cognee)

## Improve The Wiki

When an answer misses an important connection, record feedback and apply a focused improvement:

```bash
python3 scripts/improve.py --feedback examples/feedback/software-2-nanogpt-llmc.json --apply
```

This updates relevant wiki pages and can also store the improvement record in Cognee with `--graph`.

## Check Health

Run the wiki lint before publishing or after bulk ingestion:

```bash
python3 scripts/lint_wiki.py
```

The linter checks frontmatter, source IDs, broken wiki links, duplicate aliases, unresolved action markers, and optional orphan pages.

Run the stricter publishing check when editing sourced pages:

```bash
python3 scripts/lint_wiki.py --strict-citations --semantic
```

The stricter check also validates claim-level citations, weak source grounding, contradiction risks, and staleness-sensitive wording.
