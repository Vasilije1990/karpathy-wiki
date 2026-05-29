#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.request import Request, urlopen

from wiki_common import (
    DEFAULT_DATASET,
    RAW_DIR,
    WIKI_DIR,
    append_log,
    cognee_remember,
    run_async,
    search_markdown,
    slugify,
    source_id_from_path_or_url,
    today,
    write_session_event,
    write_text,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest one source into the Karpathy wiki.")
    parser.add_argument("source", help="Local source path or URL")
    parser.add_argument("--session", default="karpathy-wiki-ingest", help="Cognee session id")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Cognee dataset name")
    parser.add_argument("--title", default=None, help="Override source title")
    parser.add_argument("--source-id", default=None, help="Override source id")
    parser.add_argument("--graph", action="store_true", help="Also promote durable memory into Cognee graph")
    parser.add_argument(
        "--memory-only",
        action="store_true",
        help="Do not write raw/wiki/log files; only exercise Cognee/session memory paths",
    )
    args = parser.parse_args()

    source_text, source_title, source_url = read_source(args.source, args.title)
    source_id = args.source_id or infer_source_id(source_text) or source_id_from_path_or_url(args.source)
    title = source_title or source_id.replace("-", " ").title()

    raw_path = RAW_DIR / f"{source_id}.md"
    if not args.memory_only and not raw_path.exists():
        write_text(
            raw_path,
            "\n".join(
                [
                    f"# Source: {title}",
                    "",
                    f"source_id: {source_id}",
                    f"title: {title}",
                    f"url: {source_url or ''}",
                    "status: captured",
                    f"captured: {today()}",
                    "",
                    "## Content",
                    "",
                    source_text.strip()[:8000],
                ]
            ),
        )

    note_path = WIKI_DIR / "source-notes" / f"{source_id}.md"
    if not args.memory_only and not note_path.exists():
        note_body = build_source_note_body(source_id, title, source_url, source_text)
        write_text(note_path, note_body)

    related = search_markdown(title + "\n" + source_text, limit=6)
    session_event_status = write_session_event(
        args.session,
        {
            "kind": "ingest",
            "source_id": source_id,
            "title": title,
            "related_pages": [page.relative_path for page, _, _ in related],
        },
    )

    durable_memory = json.dumps(
        {
            "kind": "karpathy-wiki-source",
            "source_id": source_id,
            "title": title,
            "url": source_url or "",
            "summary": summarize(source_text),
            "candidate_claims": claims(source_text),
            "tags": keyword_tags(source_text),
            "related_pages": [
                {"path": page.relative_path, "snippet": snippet}
                for page, _, snippet in related
            ],
            "memory_policy": "Use this as recalled context. Factual answers must cite the source_id or source note.",
        },
        ensure_ascii=False,
        indent=2,
    )
    session_status = run_async(cognee_remember(durable_memory, args.dataset, session_id=args.session))
    graph_status = (
        run_async(cognee_remember(durable_memory, args.dataset, session_id=None))
        if args.graph
        else "cognee graph skipped: pass --graph when LLM/network access is configured"
    )

    if not args.memory_only:
        append_log(
            "ingest",
            title,
            f"Added source `{source_id}` and source note `wiki/source-notes/{source_id}.md`.",
        )

    print(f"ingested: {title}")
    print(f"source id: {source_id}")
    print(f"raw path: {raw_path.relative_to(WIKI_DIR.parents[0])}")
    print(f"source note: {note_path.relative_to(WIKI_DIR.parents[0])}")
    if args.memory_only:
        print("file writes: skipped by --memory-only")
    print(session_event_status)
    print(session_status)
    print(graph_status)


def read_source(source: str, title: str | None) -> tuple[str, str | None, str | None]:
    if source.startswith(("http://", "https://")):
        request = Request(source, headers={"User-Agent": "karpathy-wiki-ingestor/0.1"})
        with urlopen(request, timeout=15) as response:
            text = response.read().decode("utf-8", errors="replace")
        return text, title or infer_title(text), source

    path = Path(source)
    text = path.read_text(encoding="utf-8")
    return text, title or infer_title(text) or path.stem.replace("-", " ").title(), None


def infer_title(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip()
    return None


def infer_source_id(text: str) -> str | None:
    for line in text.splitlines()[:20]:
        if line.lower().startswith("source_id:"):
            return slugify(line.split(":", 1)[1].strip())
    return None


def summarize(text: str) -> str:
    paragraphs = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]
    return " ".join(paragraphs[:3])[:900]


def build_source_note_body(source_id: str, title: str, url: str | None, text: str) -> str:
    summary = summarize(text)
    tags = sorted(set(["source-note", "ingested", *keyword_tags(text)]))
    tag_lines = "\n".join(f"  - {tag}" for tag in tags)
    source_url = url or f"raw/sources/{source_id}.md"
    body_title = title.replace(":", "-")

    return f"""---
title: Source Note - {body_title}
type: source-note
status: draft
created: {today()}
updated: {today()}
sources:
  - {source_id}
tags:
{tag_lines}
aliases:
  - {body_title}
related:
  - ../index.md
confidence: medium
---

# Source Note - {title}

## Source

- Source ID: `{source_id}`
- URL or local record: {source_url}

## Summary

{summary or "No summary extracted yet."}

## Candidate Claims

{claim_lines(text)}

## Open Questions

- Which existing wiki pages should this source update?
- Does this source introduce a new concept, project, or timeline event?
"""


def keyword_tags(text: str) -> list[str]:
    lower = text.lower()
    candidates = {
        "agents": "agents",
        "wiki": "wiki",
        "gpt": "transformers",
        "transformer": "transformers",
        "neural": "neural-networks",
        "software": "software-2-0",
        "education": "education",
        "course": "education",
    }
    return [tag for keyword, tag in candidates.items() if keyword in lower]


def claim_lines(text: str) -> str:
    sentences = claims(text)
    if not sentences:
        return "- No candidate claims extracted yet."
    return "\n".join(f"- {sentence}" for sentence in sentences)


def claims(text: str) -> list[str]:
    sentences = []
    for chunk in text.replace("\n", " ").split(". "):
        stripped = chunk.strip()
        if 40 <= len(stripped) <= 240:
            sentences.append(stripped.rstrip(".") + ".")
        if len(sentences) == 5:
            break
    return sentences


if __name__ == "__main__":
    main()
