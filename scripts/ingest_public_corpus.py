#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from wiki_common import (
    DEFAULT_DATASET,
    RAW_DIR,
    WIKI_DIR,
    append_log,
    cognee_remember_many,
    run_async,
    search_markdown,
    today,
    write_session_event,
    write_text,
)


@dataclass(frozen=True)
class CorpusSource:
    source_id: str
    title: str
    url: str
    kind: str
    tags: tuple[str, ...]
    related: tuple[str, ...]


SOURCES: tuple[CorpusSource, ...] = (
    CorpusSource(
        "nanogpt-readme",
        "nanoGPT README",
        "https://raw.githubusercontent.com/karpathy/nanoGPT/master/README.md",
        "github-readme",
        ("source-note", "project", "transformers", "education"),
        ("../projects/nanogpt.md", "../concepts/education.md"),
    ),
    CorpusSource(
        "mingpt-readme",
        "minGPT README",
        "https://raw.githubusercontent.com/karpathy/minGPT/master/README.md",
        "github-readme",
        ("source-note", "project", "transformers", "education"),
        ("../projects/mingpt.md", "../concepts/education.md"),
    ),
    CorpusSource(
        "llm-c-readme",
        "llm.c README",
        "https://raw.githubusercontent.com/karpathy/llm.c/master/README.md",
        "github-readme",
        ("source-note", "project", "systems", "llm"),
        ("../projects/llm-c.md", "../concepts/software-2-0.md"),
    ),
    CorpusSource(
        "cs231n-course",
        "CS231n Course Site",
        "https://cs231n.stanford.edu/",
        "course-site",
        ("source-note", "course", "computer-vision", "education"),
        ("../projects/cs231n.md", "../concepts/neural-networks.md"),
    ),
    CorpusSource(
        "cs231n-notes",
        "CS231n Notes",
        "https://cs231n.github.io/",
        "course-notes",
        ("source-note", "course", "notes", "education"),
        ("../projects/cs231n.md", "../concepts/neural-networks.md"),
    ),
    CorpusSource(
        "software-2-0-essay",
        "Software 2.0 Essay",
        "https://karpathy.medium.com/software-2-0-a64152b37c35",
        "essay",
        ("source-note", "software-2-0", "systems", "neural-networks"),
        ("../concepts/software-2-0.md", "../concepts/neural-networks.md"),
    ),
    CorpusSource(
        "rnn-effectiveness",
        "The Unreasonable Effectiveness of Recurrent Neural Networks",
        "https://karpathy.github.io/2015/05/21/rnn-effectiveness/",
        "essay",
        ("source-note", "rnn", "neural-networks", "education"),
        ("../concepts/neural-networks.md", "../concepts/education.md"),
    ),
    CorpusSource(
        "training-nn-recipe",
        "A Recipe for Training Neural Networks",
        "https://karpathy.github.io/2019/04/25/recipe/",
        "essay",
        ("source-note", "training", "neural-networks", "education"),
        ("../concepts/neural-networks.md", "../concepts/education.md"),
    ),
    CorpusSource(
        "hacker-guide-neural-networks",
        "Hacker's Guide to Neural Networks",
        "https://karpathy.github.io/neuralnets/",
        "tutorial",
        ("source-note", "neural-networks", "tutorial", "education"),
        ("../concepts/neural-networks.md", "../concepts/education.md"),
    ),
    CorpusSource(
        "deep-rl-pong",
        "Deep Reinforcement Learning: Pong from Pixels",
        "https://karpathy.github.io/2016/05/31/rl/",
        "essay",
        ("source-note", "reinforcement-learning", "neural-networks", "education"),
        ("../concepts/neural-networks.md", "../concepts/education.md"),
    ),
    CorpusSource(
        "karpathy-homepage",
        "Andrej Karpathy Homepage",
        "https://karpathy.ai/",
        "homepage",
        ("source-note", "person", "public-work", "index"),
        ("../people/andrej-karpathy.md", "../timeline.md"),
    ),
    CorpusSource(
        "karpathy-blog-index",
        "Andrej Karpathy Blog Index",
        "https://karpathy.github.io/",
        "blog-index",
        ("source-note", "blog", "public-work", "index"),
        ("../people/andrej-karpathy.md", "../timeline.md"),
    ),
    CorpusSource(
        "micrograd-readme",
        "micrograd README",
        "https://raw.githubusercontent.com/karpathy/micrograd/master/README.md",
        "github-readme",
        ("source-note", "project", "autograd", "education"),
        ("../concepts/neural-networks.md", "../concepts/education.md"),
    ),
    CorpusSource(
        "makemore-readme",
        "makemore README",
        "https://raw.githubusercontent.com/karpathy/makemore/master/README.md",
        "github-readme",
        ("source-note", "project", "education", "language-modeling"),
        ("../concepts/education.md", "../concepts/neural-networks.md"),
    ),
    CorpusSource(
        "nanochat-readme",
        "nanochat README",
        "https://raw.githubusercontent.com/karpathy/nanochat/master/README.md",
        "github-readme",
        ("source-note", "project", "llm", "education"),
        ("../projects/nanogpt.md", "../concepts/agents.md"),
    ),
    CorpusSource(
        "char-rnn-readme",
        "char-rnn README",
        "https://raw.githubusercontent.com/karpathy/char-rnn/master/README.md",
        "github-readme",
        ("source-note", "project", "rnn", "language-modeling"),
        ("../concepts/neural-networks.md", "../concepts/education.md"),
    ),
    CorpusSource(
        "neuraltalk2-readme",
        "neuraltalk2 README",
        "https://raw.githubusercontent.com/karpathy/neuraltalk2/master/README.md",
        "github-readme",
        ("source-note", "project", "computer-vision", "neural-networks"),
        ("../concepts/neural-networks.md", "../projects/cs231n.md"),
    ),
    CorpusSource(
        "convnetjs-readme",
        "ConvNetJS README",
        "https://raw.githubusercontent.com/karpathy/convnetjs/master/README.md",
        "github-readme",
        ("source-note", "project", "neural-networks", "education"),
        ("../concepts/neural-networks.md", "../concepts/education.md"),
    ),
)


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.links: list[tuple[str, str]] = []
        self.blocks: list[str] = []
        self._stack: list[str] = []
        self._buffer: list[str] = []
        self._href: str | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        self._stack.append(tag)
        if tag in {"p", "li", "h1", "h2", "h3", "title"}:
            self._buffer = []
        if tag == "a":
            attrs_dict = dict(attrs)
            self._href = attrs_dict.get("href")

    def handle_endtag(self, tag: str) -> None:
        text = normalize_space("".join(self._buffer))
        if text:
            if tag == "title":
                self.title = html.unescape(text)
            elif tag in {"p", "li", "h1", "h2", "h3"}:
                self.blocks.append(html.unescape(text))
            elif tag == "a" and self._href:
                self.links.append((html.unescape(text), self._href))
        if tag == "a":
            self._href = None
        if self._stack:
            self._stack.pop()
        if tag in {"p", "li", "h1", "h2", "h3", "title"}:
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if any(tag in {"script", "style", "noscript"} for tag in self._stack):
            return
        if self._stack and self._stack[-1] in {"p", "li", "h1", "h2", "h3", "title", "a"}:
            self._buffer.append(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and ingest the curated public Karpathy corpus.")
    parser.add_argument("--session", default="karpathy-wiki-corpus", help="Cognee session id")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Cognee dataset name")
    parser.add_argument("--graph", action="store_true", help="Promote compact source summaries into Cognee graph")
    parser.add_argument("--limit", type=int, default=0, help="Only ingest the first N sources")
    args = parser.parse_args()

    selected = SOURCES[: args.limit] if args.limit else SOURCES
    successes: list[str] = []
    failures: list[str] = []
    memory_items: list[str] = []

    for source in selected:
        try:
            record = fetch_source(source)
            write_raw_source(source, record)
            write_source_note(source, record)
            memory_items.append(build_source_memory(source, record))
            successes.append(f"{source.source_id}: source files captured")
            print(f"captured {source.source_id}")
        except Exception as exc:
            write_failure_placeholder(source, exc)
            failures.append(f"{source.source_id}: {exc}")
            print(f"failed {source.source_id}: {exc}")

    if memory_items:
        session_status = run_async(cognee_remember_many(memory_items, args.dataset, session_id=args.session))
        graph_status = (
            run_async(cognee_remember_many(memory_items, args.dataset, session_id=None))
            if args.graph
            else "cognee graph skipped: pass --graph when LLM/network access is configured"
        )
    else:
        session_status = "cognee skipped: no memory items"
        graph_status = "cognee skipped: no memory items"

    write_session_event(
        args.session,
        {
            "kind": "public-corpus-ingest",
            "successes": successes,
            "failures": failures,
            "session_status": session_status,
            "graph_status": graph_status,
        },
    )
    append_log(
        "ingest",
        "public Karpathy corpus",
        f"Ingested {len(successes)} public source records. Failures: {len(failures)}.",
    )

    print()
    print(session_status)
    print(graph_status)
    print(f"completed: {len(successes)} succeeded, {len(failures)} failed")
    for failure in failures:
        print(f"- {failure}")


def fetch_source(source: CorpusSource) -> dict:
    request = Request(source.url, headers={"User-Agent": "karpathy-wiki-corpus/0.1"})
    with urlopen(request, timeout=20) as response:
        content_type = response.headers.get("content-type", "")
        raw = response.read().decode("utf-8", errors="replace")

    if "html" in content_type or source.url.endswith("/"):
        extracted = extract_html(raw)
    else:
        extracted = extract_markdown(raw)

    return {
        "content_type": content_type,
        "raw": raw,
        **extracted,
    }


def extract_markdown(raw: str) -> dict:
    headings = [line.lstrip("# ").strip() for line in raw.splitlines() if line.startswith("#")]
    paragraphs = [
        normalize_space(line)
        for line in raw.splitlines()
        if line.strip() and not line.startswith("#") and not line.strip().startswith(("[", "!", "<"))
    ]
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", raw)
    return {
        "page_title": headings[0] if headings else "",
        "headings": headings[:12],
        "paragraphs": paragraphs[:30],
        "links": links[:20],
    }


def extract_html(raw: str) -> dict:
    parser = TextExtractor()
    parser.feed(raw)
    headings = [block for block in parser.blocks if 3 <= len(block) <= 120][:12]
    paragraphs = [block for block in parser.blocks if 40 <= len(block) <= 700][:30]
    return {
        "page_title": parser.title,
        "headings": headings,
        "paragraphs": paragraphs,
        "links": parser.links[:20],
    }


def write_raw_source(source: CorpusSource, record: dict) -> None:
    excerpt = "\n\n".join(record["paragraphs"][:12])
    headings = "\n".join(f"- {heading}" for heading in record["headings"][:12]) or "- No headings extracted."
    content = f"""# Source: {source.title}

source_id: {source.source_id}
title: {source.title}
url: {source.url}
kind: {source.kind}
status: captured-as-excerpt
captured: {today()}

## Extracted Headings

{headings}

## Excerpt

{excerpt or "No excerpt extracted."}

## Capture Policy

This source record stores metadata, headings, and excerpts for wiki synthesis. It does not attempt to mirror the full upstream page.
"""
    write_text(RAW_DIR / f"{source.source_id}.md", content)


def write_source_note(source: CorpusSource, record: dict) -> None:
    tag_lines = "\n".join(f"  - {tag}" for tag in source.tags)
    source_lines = f"  - {source.source_id}"
    related_lines = "\n".join(f"  - {path}" for path in source.related)
    headings = "\n".join(f"- {heading}" for heading in record["headings"][:10]) or "- No headings extracted."
    observations = candidate_observations(record["paragraphs"])
    links = "\n".join(
        f"- [{text}]({urljoin(source.url, href)})" for text, href in record["links"][:8]
    ) or "- No links extracted."

    content = f"""---
title: Source Note - {source.title}
type: source-note
status: draft
created: {today()}
updated: {today()}
sources:
{source_lines}
tags:
{tag_lines}
aliases:
  - {source.title}
related:
{related_lines}
confidence: medium
---

# Source Note - {source.title}

## Source

- Source ID: `{source.source_id}`
- URL: {source.url}
- Kind: {source.kind}

## Extracted Headings

{headings}

## Candidate Observations

{observations}

## Useful Links

{links}

## Follow-Up

- Decide which topic or project pages should absorb this source.
- Add source-backed claims to related pages after reviewing the upstream source.
"""
    write_text(WIKI_DIR / "source-notes" / f"{source.source_id}.md", content)


def write_failure_placeholder(source: CorpusSource, exc: Exception) -> None:
    raw_path = RAW_DIR / f"{source.source_id}.md"
    note_path = WIKI_DIR / "source-notes" / f"{source.source_id}.md"
    if raw_path.exists() and note_path.exists():
        return

    raw_content = f"""# Source: {source.title}

source_id: {source.source_id}
title: {source.title}
url: {source.url}
kind: {source.kind}
status: fetch-failed-placeholder
captured: {today()}

## Fetch Failure

- {exc}

## Capture Policy

This placeholder records that the source was part of the curated corpus but could not be fetched from the configured URL during ingestion. Resolve the canonical URL before extracting claims.
"""
    note_content = f"""---
title: Source Note - {source.title}
type: source-note
status: seed
created: {today()}
updated: {today()}
sources:
  - {source.source_id}
tags:
{chr(10).join(f"  - {tag}" for tag in source.tags)}
aliases:
  - {source.title}
related:
{chr(10).join(f"  - {path}" for path in source.related)}
confidence: low
---

# Source Note - {source.title}

## Source

- Source ID: `{source.source_id}`
- URL: {source.url}
- Kind: {source.kind}
- Status: fetch-failed-placeholder

## Fetch Failure

- {exc}

## Follow-Up

- Resolve the canonical upstream URL.
- Extract source-backed observations only after the source is fetched.
"""
    if not raw_path.exists():
        write_text(raw_path, raw_content)
    if not note_path.exists():
        write_text(note_path, note_content)


def build_source_memory(
    source: CorpusSource,
    record: dict,
) -> str:
    related = search_markdown(source.title + "\n" + "\n".join(record["paragraphs"][:5]), limit=5)
    related_summary = "\n".join(f"- {page.relative_path}: {snippet}" for page, _, snippet in related)
    return f"""
Karpathy wiki public corpus source.
source_id: {source.source_id}
title: {source.title}
url: {source.url}
kind: {source.kind}
headings:
{chr(10).join("- " + heading for heading in record["headings"][:8])}
summary:
{summarize(record["paragraphs"])}
related_pages:
{related_summary}
"""


def candidate_observations(paragraphs: list[str]) -> str:
    observations = []
    for paragraph in paragraphs:
        cleaned = normalize_space(paragraph)
        if 50 <= len(cleaned) <= 260:
            observations.append(cleaned)
        if len(observations) == 6:
            break
    if not observations:
        return "- No candidate observations extracted."
    return "\n".join(f"- {item}" for item in observations)


def summarize(paragraphs: list[str]) -> str:
    return " ".join(paragraphs[:4])[:1200] or "No summary extracted."


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


if __name__ == "__main__":
    main()
