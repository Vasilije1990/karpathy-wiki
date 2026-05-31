---
title: Generate Your Own Wiki
type: overview
status: reviewed
created: 2026-05-31
updated: 2026-05-31
sources:
  - llm-wiki-gist
  - karpathy-wiki-operating-schema
  - cognee-resources
tags:
  - guide
  - wiki-generation
  - cognee
  - starter
aliases:
  - Make Your Own Wiki
  - Wiki Generator
related:
  - index.md
  - how-to-use.md
  - concepts/llm-wiki.md
  - source-notes/cognee-resources.md
confidence: high
---

# Generate Your Own Wiki

This repository can be reused as a fresh LLM wiki engine. The reusable pattern is source-first: keep raw evidence under `raw/sources/`, write readable pages under `wiki/`, and use Cognee when you want durable memory, graph recall, and query synthesis. (sources: `llm-wiki-gist`, `karpathy-wiki-operating-schema`, `cognee-resources`)

## Fast Path

From this repository, generate a standalone experimental project:

```bash
python3 scripts/create_wiki_project.py ../my-experimental-wiki --title "My Experimental Wiki" --topic "the domain I want to study"
cd ../my-experimental-wiki
npm install
npm run dev
```

The generated project includes the Vite wiki website, seed markdown pages, raw source folders, maintenance scripts, local query API, and Cognee-ready defaults.

## Add Cognee Memory

Set filesystem-backed session memory for local runs:

```bash
export CACHING=true
export CACHE_BACKEND=fs
```

Install the Python workflow dependencies:

```bash
uv venv
uv pip install -e .
```

Ingest a source into the generated wiki:

```bash
uv run scripts/ingest.py raw/sources/seed.md --session my-wiki-ingest --dataset my-experimental-wiki
```

Add `--graph` when provider access is configured and you want compact source summaries promoted into durable Cognee graph memory.

## Ask And File Answers

Run the local API:

```bash
npm run api
```

Then use the website's `Ask Cognee` tab, or use the terminal:

```bash
uv run scripts/query.py "What should this wiki explain first?" --session my-wiki-query --dataset my-experimental-wiki --file-answer --reviewed
```

Reviewed answers are filed under `wiki/source-notes/` so useful synthesis becomes part of the wiki.

## Reuse The Starter Only

For a minimal content-only scaffold, copy `examples/experimental-wiki-starter/`. That folder contains seed `AGENTS.md`, `raw/sources/`, `wiki/`, source-note, guide, and log files that can be reused without the Vite website.

## Publish Checklist

- Replace the seed source with real source records.
- Update `src/site-config.ts` with your wiki title, description, keywords, and notice settings.
- Keep Cognee links visible so readers can inspect the memory layer: [website](https://www.cognee.ai/), [docs](https://docs.cognee.ai/), and [GitHub](https://github.com/topoteretes/cognee). (source: `cognee-resources`)
- Run `uv run scripts/lint_wiki.py --strict-citations --semantic`.
- Run `npm run build`.
