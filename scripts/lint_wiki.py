#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from wiki_common import (
    RAW_DIR,
    REQUIRED_FRONTMATTER,
    WIKI_DIR,
    extract_markdown_links,
    load_pages,
    list_value,
    resolve_wiki_link,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint the Karpathy wiki markdown files.")
    parser.add_argument("--strict-orphans", action="store_true", help="Fail on orphan pages")
    parser.add_argument("--strict-citations", action="store_true", help="Require claim-level source citations on claim-bearing pages")
    parser.add_argument("--semantic", action="store_true", help="Run semantic source-grounding, contradiction, and staleness checks")
    args = parser.parse_args()

    pages = load_pages()
    page_paths = {page.relative_path for page in pages}
    source_index = build_source_index(pages)
    findings: list[str] = []

    findings.extend(check_frontmatter(pages))
    findings.extend(check_links(pages, page_paths))
    findings.extend(check_duplicates(pages))
    findings.extend(check_todos(pages))
    if args.strict_citations:
        findings.extend(check_source_ids(pages, source_index))
        findings.extend(check_claim_citations(pages))
    if args.semantic:
        findings.extend(check_semantic_consistency(pages, source_index))
    orphan_findings = check_orphans(pages)
    if args.strict_orphans:
        findings.extend(orphan_findings)

    if findings:
        print("Wiki lint findings:")
        for finding in findings:
            print(f"- {finding}")
        if orphan_findings and not args.strict_orphans:
            print()
            print("Orphan warnings:")
            for finding in orphan_findings:
                print(f"- {finding}")
        raise SystemExit(1)

    print(f"Wiki lint passed: {len(pages)} pages checked.")
    if orphan_findings:
        print("Orphan warnings:")
        for finding in orphan_findings:
            print(f"- {finding}")


def check_frontmatter(pages) -> list[str]:
    findings: list[str] = []
    for page in pages:
        missing = [key for key in REQUIRED_FRONTMATTER if key not in page.frontmatter]
        if missing:
            findings.append(f"{page.relative_path}: missing frontmatter keys: {', '.join(missing)}")
        if not list_value(page.frontmatter.get("sources")):
            findings.append(f"{page.relative_path}: missing source ids")
        if not page.body.strip():
            findings.append(f"{page.relative_path}: empty body")
    return findings


def check_links(pages, page_paths: set[str]) -> list[str]:
    findings: list[str] = []
    for page in pages:
        links = wiki_body_links(page.body) + list_value(page.frontmatter.get("related"))
        for href in links:
            resolved = resolve_wiki_link(page.relative_path, href)
            if resolved and resolved not in page_paths:
                findings.append(f"{page.relative_path}: broken link `{href}` -> `{resolved}`")
    return findings


def check_duplicates(pages) -> list[str]:
    seen: dict[str, list[str]] = defaultdict(list)
    for page in pages:
        for value in [page.title, *page.aliases]:
            seen[value.lower()].append(page.relative_path)

    return [
        f"duplicate title/alias `{value}` in {', '.join(paths)}"
        for value, paths in seen.items()
        if len(paths) > 1
    ]


def check_todos(pages) -> list[str]:
    findings: list[str] = []
    for page in pages:
        if "TODO" in page.body:
            findings.append(f"{page.relative_path}: contains TODO")
    return findings


def check_source_ids(pages, source_index: dict[str, str]) -> list[str]:
    findings: list[str] = []
    allowed_missing = {"query-synthesis"}
    for page in pages:
        for source_id in page.sources:
            if source_id not in source_index and source_id not in allowed_missing:
                findings.append(f"{page.relative_path}: source id `{source_id}` has no raw/source-note record")
    return findings


def check_claim_citations(pages) -> list[str]:
    findings: list[str] = []
    for page in pages:
        if not requires_source_backed_claims(page):
            continue

        claims = source_backed_claims(page)
        if not claims:
            findings.append(f"{page.relative_path}: missing `## Source-Backed Claims` bullets")
            continue

        page_sources = set(page.sources)
        for claim in claims:
            cited = set(claim.source_ids)
            if not cited:
                findings.append(f"{page.relative_path}:{claim.line_no}: claim is missing inline source ids")
            elif not cited.issubset(page_sources):
                missing = ", ".join(sorted(cited - page_sources))
                findings.append(f"{page.relative_path}:{claim.line_no}: claim cites source ids not listed in frontmatter: {missing}")
    return findings


def check_orphans(pages) -> list[str]:
    incoming: dict[str, int] = {page.relative_path: 0 for page in pages}
    for page in pages:
        links = wiki_body_links(page.body) + list_value(page.frontmatter.get("related"))
        for href in links:
            resolved = resolve_wiki_link(page.relative_path, href)
            if resolved in incoming and resolved != page.relative_path:
                incoming[resolved] += 1

    allowed = {"index.md"}
    return [
        f"{path}: no inbound wiki links"
        for path, count in sorted(incoming.items())
        if count == 0 and path not in allowed
    ]


def wiki_body_links(body: str) -> list[str]:
    return [
        href
        for href in extract_markdown_links(body)
        if href.endswith(".md") or href.startswith(("#", "wiki/"))
    ]


def build_source_index(pages) -> dict[str, str]:
    source_index: dict[str, str] = {}
    for path in RAW_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^source_id:\s*([A-Za-z0-9_.-]+)\s*$", text, flags=re.MULTILINE)
        if match:
            source_index[match.group(1)] = text
    for page in pages:
        if page.frontmatter.get("type") == "source-note":
            for source_id in page.sources:
                source_index.setdefault(source_id, page.raw)
    return source_index


def requires_source_backed_claims(page) -> bool:
    page_type = page.frontmatter.get("type")
    return page_type in {"person", "concept", "project", "timeline"}


@dataclass(frozen=True)
class SourceClaim:
    page_path: str
    line_no: int
    text: str
    source_ids: list[str]


def source_backed_claims(page) -> list[SourceClaim]:
    lines = page.body.splitlines()
    in_section = False
    claims: list[SourceClaim] = []
    for line_no, line in enumerate(lines, start=1):
        if line.strip() == "## Source-Backed Claims":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("- "):
            claims.append(
                SourceClaim(
                    page.relative_path,
                    line_no,
                    line.strip(),
                    re.findall(r"`([A-Za-z0-9_.-]+)`", line),
                )
            )
    return claims


def check_semantic_consistency(pages, source_index: dict[str, str]) -> list[str]:
    findings: list[str] = []
    claims = [claim for page in pages for claim in source_backed_claims(page)]
    findings.extend(check_claim_grounding(claims, source_index))
    findings.extend(check_staleness_language(pages))
    findings.extend(check_claim_contradictions(claims))
    findings.extend(check_future_dates(pages))
    return findings


def check_claim_grounding(claims: list[SourceClaim], source_index: dict[str, str]) -> list[str]:
    findings: list[str] = []
    for claim in claims:
        claim_terms = significant_terms(strip_citations(claim.text))
        if not claim_terms or not claim.source_ids:
            continue

        source_text = " ".join(source_index.get(source_id, "") for source_id in claim.source_ids).lower()
        if not source_text:
            continue

        overlap = [term for term in claim_terms if term in source_text]
        threshold = 2 if len(claim_terms) <= 8 else 3
        if len(overlap) < threshold:
            findings.append(
                f"{claim.page_path}:{claim.line_no}: weak source grounding for claim; "
                f"only matched {len(overlap)} significant terms in cited source text"
            )
    return findings


def check_staleness_language(pages) -> list[str]:
    findings: list[str] = []
    stale_terms = re.compile(r"\b(currently|latest|recently|now|today|newest)\b", flags=re.IGNORECASE)
    dated = re.compile(r"\b(?:19|20)\d{2}(?:-\d{2}-\d{2})?\b")
    for page in pages:
        if page.frontmatter.get("type") in {"source-note", "log"}:
            continue
        for line_no, line in enumerate(page.body.splitlines(), start=1):
            if line.lstrip().startswith("#"):
                continue
            if not stale_terms.search(line):
                continue
            if dated.search(line) or "(source:" in line or "(sources:" in line:
                continue
            findings.append(f"{page.relative_path}:{line_no}: staleness-sensitive wording needs a date and source citation")
    return findings


def check_claim_contradictions(claims: list[SourceClaim]) -> list[str]:
    findings: list[str] = []
    status_terms = {
        "active": re.compile(r"\b(active|ongoing|maintained|current)\b", flags=re.IGNORECASE),
        "inactive": re.compile(r"\b(archived|deprecated|inactive|unmaintained|superseded)\b", flags=re.IGNORECASE),
    }
    by_subject: dict[str, set[str]] = defaultdict(set)
    locations: dict[tuple[str, str], list[str]] = defaultdict(list)
    for claim in claims:
        subject = likely_subject(claim.text)
        if not subject:
            continue
        for status, pattern in status_terms.items():
            if pattern.search(claim.text):
                by_subject[subject].add(status)
                locations[(subject, status)].append(f"{claim.page_path}:{claim.line_no}")

    for subject, statuses in by_subject.items():
        if {"active", "inactive"}.issubset(statuses):
            active_locations = ", ".join(locations[(subject, "active")])
            inactive_locations = ", ".join(locations[(subject, "inactive")])
            findings.append(
                f"semantic contradiction risk for `{subject}`: active claims at {active_locations}; "
                f"inactive claims at {inactive_locations}"
            )
    return findings


def check_future_dates(pages) -> list[str]:
    findings: list[str] = []
    current_year = date.today().year
    for page in pages:
        for match in re.finditer(r"\b(20\d{2})\b", page.body):
            year = int(match.group(1))
            if year > current_year:
                line_no = page.body[: match.start()].count("\n") + 1
                findings.append(f"{page.relative_path}:{line_no}: future year `{year}` needs explicit future/planned wording")
    return findings


def strip_citations(value: str) -> str:
    return re.sub(r"\(sources?:\s*[^)]+\)", "", value)


def significant_terms(value: str) -> list[str]:
    stopwords = {
        "about",
        "across",
        "also",
        "and",
        "are",
        "because",
        "between",
        "claim",
        "connects",
        "from",
        "into",
        "that",
        "the",
        "their",
        "this",
        "through",
        "with",
    }
    terms = [
        term
        for term in re.findall(r"[a-z0-9.]{4,}", value.lower())
        if term not in stopwords and not term.isdigit()
    ]
    return list(dict.fromkeys(terms))


def likely_subject(claim: str) -> str:
    text = strip_citations(claim)
    text = re.sub(r"^-+\s*", "", text).strip()
    for delimiter in (" is ", " are ", " was ", " were ", " frames ", " describes ", " presents "):
        if delimiter in text:
            subject = text.split(delimiter, 1)[0]
            break
    else:
        subject = text.split(",", 1)[0]
    subject = re.sub(r"[^A-Za-z0-9. ]+", "", subject).strip().lower()
    words = subject.split()
    return " ".join(words[:5])


if __name__ == "__main__":
    main()
