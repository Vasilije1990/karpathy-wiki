#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from wiki_common import ROOT, slugify, today


ENGINE_PATHS = [
    "index.html",
    "package.json",
    "package-lock.json",
    "pyproject.toml",
    "tsconfig.json",
    "vite.config.ts",
    "src",
    "scripts",
    "skills",
    "public",
    "LICENSE",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a fresh experimental LLM wiki project.")
    parser.add_argument("target", help="Directory for the new wiki project")
    parser.add_argument("--title", default="Experimental LLM Wiki", help="Website and wiki title")
    parser.add_argument("--topic", default="a topic you want to research", help="Short topic description")
    parser.add_argument("--dataset", default=None, help="Cognee dataset name")
    parser.add_argument("--force", action="store_true", help="Allow overwriting generated starter files")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    if target == ROOT:
        raise SystemExit("Refusing to generate over the source repository; choose a new target directory")
    title = args.title.strip()
    topic = args.topic.strip()
    slug = slugify(title)
    dataset = args.dataset or slug

    ensure_target(target, args.force)
    copy_engine(target)
    remove_project_specific_files(target)
    write_project_files(target, title, topic, slug, dataset, force=args.force)
    rewrite_package(target, slug, title)
    rewrite_dataset_default(target, dataset)

    print(f"created wiki project: {target}")
    print(f"title: {title}")
    print(f"dataset: {dataset}")
    print("next steps:")
    print(f"  cd {target}")
    print("  npm install")
    print("  npm run dev")


def ensure_target(target: Path, force: bool) -> None:
    if target.exists() and any(target.iterdir()) and not force:
        raise SystemExit(f"{target} is not empty; pass --force to write starter files there")
    target.mkdir(parents=True, exist_ok=True)


def copy_engine(target: Path) -> None:
    for relative in ENGINE_PATHS:
        source = ROOT / relative
        destination = target / relative
        if not source.exists():
            continue
        if source.is_dir():
            shutil.copytree(
                source,
                destination,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", "*.pyc"),
            )
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def remove_project_specific_files(target: Path) -> None:
    for relative in [
        "scripts/create_wiki_project.py",
        "scripts/ingest_public_corpus.py",
        "examples/feedback/software-2-nanogpt-llmc.json",
        "public/dario_img.png",
    ]:
        path = target / relative
        if path.exists() and path.is_file():
            path.unlink()


def write_project_files(
    target: Path,
    title: str,
    topic: str,
    slug: str,
    dataset: str,
    force: bool,
) -> None:
    context = {
        "TITLE": title,
        "SHORT_TITLE": short_title(title),
        "TOPIC": topic,
        "SLUG": slug,
        "DATASET": dataset,
        "DATE": today(),
    }
    files = starter_templates(context)
    for relative_path, content in files.items():
        path = target / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.rstrip() + "\n", encoding="utf-8")


def rewrite_package(target: Path, slug: str, title: str) -> None:
    package_path = target / "package.json"
    if package_path.exists():
        package = json.loads(package_path.read_text(encoding="utf-8"))
        package["name"] = slug
        package["version"] = "0.1.0"
        package["private"] = True
        package_path.write_text(json.dumps(package, indent=2) + "\n", encoding="utf-8")

    lock_path = target / "package-lock.json"
    if lock_path.exists():
        lockfile = json.loads(lock_path.read_text(encoding="utf-8"))
        lockfile["name"] = slug
        if "packages" in lockfile and "" in lockfile["packages"]:
            lockfile["packages"][""]["name"] = slug
            lockfile["packages"][""]["version"] = "0.1.0"
        lock_path.write_text(json.dumps(lockfile, indent=2) + "\n", encoding="utf-8")

    pyproject_path = target / "pyproject.toml"
    pyproject_path.write_text(
        "\n".join(
            [
                "[project]",
                f'name = "{slug}"',
                'version = "0.1.0"',
                f'description = "Markdown-first LLM wiki for {title} with optional Cognee memory workflows."',
                'requires-python = ">=3.10"',
                "dependencies = [",
                '  "cognee>=1.0.0",',
                '  "python-dotenv>=1.0.0"',
                "]",
                "",
                "[project.optional-dependencies]",
                "dev = []",
                "",
                "[tool.uv]",
                "package = false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def rewrite_dataset_default(target: Path, dataset: str) -> None:
    common_path = target / "scripts" / "wiki_common.py"
    if not common_path.exists():
        return
    text = common_path.read_text(encoding="utf-8")
    text = re.sub(r'DEFAULT_DATASET = "[^"]+"', f'DEFAULT_DATASET = "{dataset}"', text)
    common_path.write_text(text, encoding="utf-8")


def starter_templates(context: dict[str, str]) -> dict[str, str]:
    title = context["TITLE"]
    short = context["SHORT_TITLE"]
    topic = context["TOPIC"]
    slug = context["SLUG"]
    dataset = context["DATASET"]
    date = context["DATE"]
    description = f"A markdown-first, Cognee-backed LLM wiki for {topic}."
    ts_description = json.dumps(description)
    ts_title = json.dumps(title)
    ts_short = json.dumps(short)
    ts_dataset = json.dumps(dataset)
    html_description = escape_html(description)
    html_title = escape_html(title)
    html_topic = escape_html(topic)

    return {
        "README.md": f"""# {title}

This is a fresh experimental LLM wiki for {topic}. It uses the same markdown-first layout as the generator project: immutable source records in `raw/sources/`, human-readable wiki pages in `wiki/`, and optional Cognee memory for recall and graph-backed synthesis.

## Start

```bash
npm install
npm run dev
```

Run the live query API in another terminal when you want the `Ask Cognee` panel:

```bash
npm run api
```

## Add A Source

Create a source record in `raw/sources/`, then ingest it:

```bash
uv venv
uv pip install -e .
export CACHING=true
export CACHE_BACKEND=fs
uv run scripts/ingest.py raw/sources/seed.md --session {slug}-ingest --dataset {dataset}
```

Add `--graph` when provider access is configured and you want durable Cognee graph memory.

## Maintain The Wiki

```bash
uv run scripts/query.py "What should this wiki explain first?" --session {slug}-query --dataset {dataset} --file-answer --reviewed
uv run scripts/lint_wiki.py --strict-citations --semantic
```
""",
        "AGENTS.md": f"""# {title} Operating Schema

This project follows the LLM Wiki pattern: raw sources are immutable, the wiki is a persistent markdown artifact, and the agent maintains page structure, links, citations, and logs.

## Layers

- `raw/sources/`: source records, metadata, excerpts, and local notes. Treat these as source of truth.
- `wiki/`: human-readable wiki pages. The agent may create and update these pages.
- `skills/`: reusable instructions for wiki maintenance workflows.
- Cognee: optional durable memory for entities, concepts, claims, summaries, relationships, contradictions, and feedback.
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

## Core Loop

1. Add source metadata or source text under `raw/sources/`.
2. Extract entities, concepts, projects, claims, dates, and open questions.
3. Write run-local observations to Cognee session memory using the active `session_id`.
4. Promote durable facts, summaries, and relationships into Cognee when provider access is configured.
5. Update or create wiki pages.
6. Update `wiki/index.md` and append to `wiki/log.md`.
""",
        "index.html": f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{html_description}" />
    <meta name="keywords" content="{html_topic}, LLM wiki, Cognee, AI memory, knowledge graph" />
    <meta name="robots" content="index, follow" />
    <meta name="theme-color" content="#f6f6f6" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="{html_title}" />
    <meta property="og:title" content="{html_title}" />
    <meta property="og:description" content="{html_description}" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="{html_title}" />
    <meta name="twitter:description" content="{html_description}" />
    <title>{html_title}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
""",
        "src/site-config.ts": f"""export const siteConfig = {{
  title: {ts_title},
  shortTitle: {ts_short},
  subtitle: "the Cognee-backed memory wiki",
  description: {ts_description},
  subjectLabel: {json.dumps(topic)},
  author: "wiki maintainer",
  dataset: {ts_dataset},
  sessionPrefix: {json.dumps(slug)},
  keywords: [
    {json.dumps(topic)},
    "LLM wiki",
    "AI memory",
    "Cognee",
    "knowledge graph",
  ],
  cogneeLinks: {{
    website: "https://www.cognee.ai/",
    docs: "https://docs.cognee.ai/",
    github: "https://github.com/topoteretes/cognee",
  }},
  noticePopup: {{
    enabled: false,
    title: "Notice",
    imageSrc: "",
    imageAlt: "",
    body: "",
  }},
}};
""",
        "src/cognee-graph.json": json.dumps(
            {
                "kind": "cognee-graph-export",
                "dataset": dataset,
                "datasetId": "",
                "exportedAt": "",
                "source": "starter",
                "nodeCount": 0,
                "edgeCount": 0,
                "nodes": [],
                "edges": [],
                "error": "No Cognee graph export is available yet.",
            },
            indent=2,
        ),
        "raw/sources/seed.md": f"""# Source: Starter Source

source_id: seed
title: Starter Source
url:
status: captured
captured: {date}

## Content

This starter source describes the initial scope for {title}: {topic}.

Replace this file with a real source record before making factual claims.
""",
        "wiki/index.md": f"""---
title: {title} Index
type: overview
status: seed
created: {date}
updated: {date}
sources:
  - seed
tags:
  - index
aliases:
  - Home
related:
  - how-to-use.md
  - source-notes/seed.md
  - log.md
confidence: low
---

# {title}

This is a seed LLM wiki for {topic}. Replace this opening page with the main thesis, topic hubs, and open questions that should guide the first ingestion run.

## Start Here

- [How To Use This Wiki](how-to-use.md)
- [Starter Source Note](source-notes/seed.md)
- [Log](log.md)

## Current Thesis

Synthesis: this wiki has not accumulated enough source-backed evidence yet. Ingest sources first, then promote stable summaries into concept, project, person, and timeline pages.

## Open Questions

- Which source set should define the first useful version of this wiki?
- Which claims need source notes before they appear in overview pages?
- Which entities and concepts should be promoted into Cognee durable memory?
""",
        "wiki/how-to-use.md": f"""---
title: How To Use This Wiki
type: overview
status: seed
created: {date}
updated: {date}
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
uv run scripts/ingest.py raw/sources/seed.md --session {slug}-ingest --dataset {dataset}
```

## Ask Questions

```bash
uv run scripts/query.py "What is this wiki about?" --session {slug}-query --dataset {dataset} --file-answer --reviewed
```

## Check Health

```bash
uv run scripts/lint_wiki.py
uv run scripts/lint_wiki.py --strict-citations --semantic
```
""",
        "wiki/source-notes/seed.md": f"""---
title: Source Note - Starter Source
type: source-note
status: seed
created: {date}
updated: {date}
sources:
  - seed
tags:
  - source-note
  - starter
aliases:
  - Starter Source Note
related:
  - ../index.md
confidence: low
---

# Source Note - Starter Source

## Source

- Source ID: `seed`
- URL or local record: raw/sources/seed.md

## Summary

This is a placeholder source note for the fresh wiki project. Replace it with real source metadata, excerpts, links, and source-backed observations.

## Open Questions

- What should be the first real source?
- Which pages should this source create or update?
""",
        "wiki/log.md": f"""---
title: Wiki Log
type: log
status: seed
created: {date}
updated: {date}
sources:
  - seed
tags:
  - log
  - operations
aliases:
  - Changelog
related:
  - index.md
confidence: high
---

# Wiki Log

## [{date}] seed | Fresh experimental wiki

Created a fresh experimental LLM wiki scaffold for {topic}.
""",
    }


def short_title(title: str) -> str:
    words = title.split()
    if len(words) <= 3:
        return title
    return " ".join(words[:3])


def escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


if __name__ == "__main__":
    main()
