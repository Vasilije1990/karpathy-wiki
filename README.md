# Andrej Karpathy Wiki

A markdown-first LLM wiki about Andrej Karpathy's public work, with Cognee as the durable memory layer and filesystem-backed Cognee session memory for ingest/query runs.

The readable artifact is the `wiki/` directory. Cognee stores structured entities, claims, summaries, relationships, and feedback records that help the wiki improve over time.

Cognee resources:

- Website: https://www.cognee.ai/
- Docs: https://docs.cognee.ai/
- GitHub: https://github.com/topoteretes/cognee

## Quickstart

```bash
npm install
npm run dev
```

Open the Vite URL printed by the command. The browser UI renders the markdown wiki with a 2000s Wikipedia-style layout and a local page graph derived from wiki links, source IDs, and tags.

For the live Cognee-backed question panel, run the API server in a second terminal:

```bash
npm run api
```

The Vite dev server proxies `/api/query` to `http://127.0.0.1:8765`. The `Ask Cognee` tab recalls Cognee memory, searches markdown evidence, and files each answer as a reviewed query synthesis page under `wiki/source-notes/`.

## Python Workflows

The scripts run in markdown-only mode if Cognee provider access is not configured. With `LLM_API_KEY` set, they use Cognee session memory via `CACHING=true` and `CACHE_BACKEND=fs`, and can write durable memory to Cognee when requested.

```bash
uv venv
uv pip install -e .

export LLM_API_KEY=<your-key>
export CACHING=true
export CACHE_BACKEND=fs

uv run scripts/ingest.py raw/sources/llm-wiki.md --session karpathy-wiki-v1
uv run scripts/ingest_public_corpus.py --session karpathy-wiki-v1 --graph
uv run scripts/query.py "What connects Software 2.0, nanoGPT, and llm.c?" --session karpathy-wiki-v1 --cognee --file-answer --reviewed
uv run scripts/lint_wiki.py --strict-citations --semantic
uv run scripts/improve.py --feedback examples/feedback/software-2-nanogpt-llmc.json --apply
```

Add `--cognee` to `query.py` when embedding/provider access is configured and you want Cognee recall folded into the answer evidence. Add `--file-answer --reviewed` to automatically persist the answer as a reviewed source note. Add `--graph` to `ingest.py`, `ingest_public_corpus.py`, or `improve.py` when LLM/network access is configured and you want durable Cognee graph promotion. Without those flags, the scripts still use markdown and filesystem-backed session events.

## Generate Your Own Wiki

Create a fresh standalone experimental wiki project from this repository:

```bash
python3 scripts/create_wiki_project.py ../my-experimental-wiki --title "My Experimental Wiki" --topic "the domain I want to study"
cd ../my-experimental-wiki
npm install
npm run dev
```

The generated project includes the Vite website, seed `raw/` and `wiki/` content, the maintenance scripts, Cognee-ready defaults, SEO metadata, and a generic `src/site-config.ts` that you can edit for your own topic.

If you only need the content schema, copy `examples/experimental-wiki-starter/`. It contains a fresh `AGENTS.md`, seed source record, source note, index, usage guide, and log that can be reused without the website engine.

## Production-Style Local Serve

```bash
npm run build
python3 scripts/wiki_server.py
```

Open `http://127.0.0.1:8765`. In this mode the Python server serves both the built frontend and the live Cognee query API.

## Structure

```text
raw/sources/       immutable source records and source metadata
wiki/              generated and maintained markdown wiki
skills/            Cognee skill prompts for wiki operations
scripts/           ingest, query, lint, and improvement workflows
src/               local browser UI over the markdown wiki
examples/          reusable starter content and feedback examples
AGENTS.md          schema and operating rules for maintaining the wiki
```

## SEO

The site includes static metadata in `index.html`, runtime per-page titles and descriptions from wiki frontmatter/body text, Open Graph and Twitter summary tags, JSON-LD structured data, semantic article markup, and `public/robots.txt`.

For a reused project, update `src/site-config.ts` before publishing so the title, description, keywords, Cognee links, and optional notice match the new wiki.

## Core Loop

1. Ingest public sources into `raw/`, Cognee filesystem session memory, Cognee durable memory, and markdown source notes.
2. Query the wiki from the website or CLI using markdown search plus Cognee recall.
3. Automatically file query answers as reviewed durable source notes when using the website API or `--file-answer --reviewed`.
4. Promote stable synthesis into concept, project, person, or timeline pages with sentence-level source IDs.
5. Run `scripts/lint_wiki.py --strict-citations --semantic` to catch missing citations, weak source grounding, contradiction risks, and staleness-sensitive wording.
