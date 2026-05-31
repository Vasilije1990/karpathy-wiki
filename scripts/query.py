#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from wiki_common import (
    DEFAULT_DATASET,
    WIKI_DIR,
    append_log,
    cognee_recall,
    run_async,
    search_markdown,
    slugify,
    today,
    write_session_event,
    write_text,
)


@dataclass(frozen=True)
class EvidenceItem:
    origin: str
    title: str
    locator: str
    snippet: str
    sources: list[str]
    score: int = 0


@dataclass(frozen=True)
class QueryResult:
    question: str
    answer: str
    evidence: list[EvidenceItem]
    cognee_status: str
    session_event_status: str
    filed_path: str | None = None


def main() -> None:
    parser = argparse.ArgumentParser(description="Query the wiki.")
    parser.add_argument("question", help="Question to answer")
    parser.add_argument("--session", default=f"{DEFAULT_DATASET}-query", help="Cognee session id")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Cognee dataset name")
    parser.add_argument("--file-answer", action="store_true", help="File the answer as a wiki source note")
    parser.add_argument("--reviewed", action="store_true", help="File query answers with reviewed status")
    parser.add_argument("--cognee", action="store_true", help="Also run Cognee recall")
    args = parser.parse_args()

    result = answer_question(
        question=args.question,
        session=args.session,
        dataset=args.dataset,
        use_cognee=args.cognee,
        file_answer_enabled=args.file_answer,
        reviewed=args.reviewed,
    )

    print(result.answer)
    print()
    print(f"[{result.session_event_status}]")
    print(f"[{result.cognee_status}]")
    if result.filed_path:
        print(f"filed: {result.filed_path}")


def answer_question(
    question: str,
    session: str | None = None,
    dataset: str = DEFAULT_DATASET,
    use_cognee: bool = False,
    file_answer_enabled: bool = False,
    reviewed: bool = False,
) -> QueryResult:
    session_id = session or f"{dataset}-query"
    hits = search_markdown(question, limit=6)
    cognee_status, memories = (
        run_async(cognee_recall(question, dataset, session_id))
        if use_cognee
        else ("cognee recall skipped: pass --cognee when embedding/provider access is configured", [])
    )

    evidence = build_evidence(hits, memories)
    answer = build_answer(question, evidence, cognee_status)
    session_event_status = write_session_event(
        session_id,
        {
            "kind": "query",
            "question": question,
            "hits": [page.relative_path for page, _, _ in hits],
            "cognee_status": cognee_status,
        },
    )

    filed_path = None
    if file_answer_enabled:
        path = file_answer(question, answer, hits, evidence, reviewed=reviewed)
        append_log(
            "query",
            question,
            f"Filed {'reviewed' if reviewed else 'draft'} answer at `{path.as_posix()}`.",
        )
        filed_path = path.as_posix()

    return QueryResult(
        question=question,
        answer=answer,
        evidence=evidence,
        cognee_status=cognee_status,
        session_event_status=session_event_status,
        filed_path=filed_path,
    )


def build_answer(question: str, evidence: list[EvidenceItem], cognee_status: str) -> str:
    lines = [
        f"# Answer: {question}",
        "",
        "## Direct Answer",
        "",
    ]

    if not evidence:
        lines.append(
            "I do not have enough wiki or Cognee context yet. Ingest more source notes, then retry the query."
        )
    else:
        lines.append(synthesize(question, evidence))

    lines.extend(["", "## Evidence", ""])
    markdown_items = [item for item in evidence if item.origin == "markdown"]
    if markdown_items:
        for item in markdown_items:
            source_text = ", ".join(item.sources) if item.sources else "no source id"
            lines.append(f"- `{item.locator}` (score {item.score}, sources: {source_text}): {item.snippet}")
    else:
        lines.append("- No markdown pages matched.")

    lines.extend(["", "## Cognee Recall", ""])
    memory_items = [item for item in evidence if item.origin == "cognee"]
    if memory_items:
        for item in memory_items[:5]:
            source_text = ", ".join(item.sources) if item.sources else "source id not found in memory"
            lines.append(f"- {item.snippet[:700]} (sources: {source_text})")
    else:
        lines.append(f"- {cognee_status}")

    source_ids = sorted({source for item in evidence for source in item.sources})
    lines.extend(["", "## Source IDs", ""])
    if source_ids:
        for source_id in source_ids:
            lines.append(f"- `{source_id}`")
    else:
        lines.append("- No source IDs were found in the matched evidence.")

    lines.extend(["", "## Filing Recommendation", ""])
    lines.append(
        "When this answer is run with `--file-answer` or through the website API, it is stored as a durable query synthesis page. "
        "Stable claims should still be promoted into the most relevant concept or project page during maintenance."
    )

    return "\n".join(lines)


def build_evidence(hits, memories: list[str]) -> list[EvidenceItem]:
    evidence: list[EvidenceItem] = []

    for page, score, snippet in hits:
        evidence.append(
            EvidenceItem(
                origin="markdown",
                title=page.title,
                locator=page.relative_path,
                snippet=snippet,
                sources=page.sources,
                score=score,
            )
        )

    for index, memory in enumerate(memories):
        evidence.append(
            EvidenceItem(
                origin="cognee",
                title=f"Cognee memory {index + 1}",
                locator=f"cognee:{index + 1}",
                snippet=compact_memory(memory),
                sources=extract_source_ids(memory),
            )
        )

    return evidence


def synthesize(question: str, evidence: list[EvidenceItem]) -> str:
    markdown_items = [item for item in evidence if item.origin == "markdown"]
    memory_items = [item for item in evidence if item.origin == "cognee"]
    if not markdown_items:
        return (
            "Cognee returned memory, but no markdown page matched. Treat the recalled memory as draft context, "
            "then file source-backed wiki pages before relying on it as durable wiki knowledge."
        )

    top_items = markdown_items[:3]
    titles = ", ".join(item.title for item in top_items)
    sources = sorted({source for item in top_items for source in item.sources})
    source_text = ", ".join(sources) if sources else "the matched wiki pages"
    memory_text = summarize_memory_items(memory_items)

    if memory_text:
        return (
            f"The strongest wiki context is in {titles}{citation_suffix(top_items)}. "
            f"Based on {source_text}, the reusable synthesis should connect those pages explicitly. "
            f"Cognee adds remembered context that points toward {memory_text}{citation_suffix(memory_items)}, "
            "so the answer should use the markdown pages for cited claims and the recalled memory for cross-page connections."
        )

    return (
        f"The strongest wiki context is in {titles}{citation_suffix(top_items)}. Based on {source_text}, "
        "the reusable synthesis should connect the relevant concepts explicitly, then point back to source notes for factual claims."
    )


def compact_memory(memory: str) -> str:
    compact = re.sub(r"\s+", " ", memory).strip()
    return compact[:1000]


def extract_source_ids(memory: str) -> list[str]:
    candidates = set(re.findall(r"source_id:\s*([a-zA-Z0-9_.-]+)", memory))
    candidates.update(re.findall(r'"source_id"\s*:\s*"([a-zA-Z0-9_.-]+)"', memory))
    candidates.update(re.findall(r"`([a-zA-Z0-9_.-]+)`", memory))
    return sorted(candidates)


def summarize_memory_items(items: list[EvidenceItem]) -> str:
    if not items:
        return ""
    source_ids = sorted({source for item in items for source in item.sources})
    if source_ids:
        return "Cognee source IDs " + ", ".join(source_ids[:5])
    words: list[str] = []
    for item in items[:3]:
        for token in re.findall(r"\b[A-Z][A-Za-z0-9_.-]+\b", item.snippet):
            if token not in words:
                words.append(token)
            if len(words) == 5:
                break
    return ", ".join(words[:5])


def citation_suffix(items: list[EvidenceItem]) -> str:
    sources = sorted({source for item in items for source in item.sources})
    if not sources:
        return ""
    label = "source" if len(sources) == 1 else "sources"
    return f" ({label}: " + ", ".join(f"`{source}`" for source in sources[:6]) + ")"


def file_answer(
    question: str,
    answer: str,
    hits,
    evidence: list[EvidenceItem],
    reviewed: bool = False,
) -> Path:
    slug = slugify(question)[:80]
    path = WIKI_DIR / "source-notes" / f"query-{slug}.md"
    sources = sorted({source for item in evidence for source in item.sources}) or ["query-synthesis"]
    source_lines = "\n".join(f"  - {source}" for source in sources)
    related_lines = "\n".join(f"  - ../{page.relative_path}" for page, _, _ in hits[:5]) or "  - ../index.md"
    status = "reviewed" if reviewed else "draft"

    content = f"""---
title: Query Synthesis - {question}
type: source-note
status: {status}
created: {today()}
updated: {today()}
sources:
{source_lines}
tags:
  - query
  - synthesis
aliases:
  - {question}
related:
{related_lines}
confidence: medium
---

<!-- auto-filed-query-answer: true -->

{answer}
"""
    write_text(path, content)
    return path.relative_to(WIKI_DIR.parents[0])


if __name__ == "__main__":
    main()
