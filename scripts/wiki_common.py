from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = ROOT / "wiki"
RAW_DIR = ROOT / "raw" / "sources"
DEFAULT_DATASET = "karpathy-wiki"
REQUIRED_FRONTMATTER = [
    "title",
    "type",
    "status",
    "created",
    "updated",
    "sources",
    "tags",
    "aliases",
    "related",
    "confidence",
]


@dataclass
class WikiPage:
    path: Path
    relative_path: str
    frontmatter: dict[str, Any]
    body: str
    raw: str

    @property
    def title(self) -> str:
        value = self.frontmatter.get("title")
        return value if isinstance(value, str) and value else title_from_path(self.path)

    @property
    def sources(self) -> list[str]:
        return list_value(self.frontmatter.get("sources"))

    @property
    def aliases(self) -> list[str]:
        return list_value(self.frontmatter.get("aliases"))


def today() -> str:
    return date.today().isoformat()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled"


def title_from_path(path: Path | str) -> str:
    name = Path(path).stem.replace("-", " ")
    return " ".join(part.capitalize() for part in name.split())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def parse_markdown(raw: str) -> tuple[dict[str, Any], str]:
    if not raw.startswith("---"):
        return {}, raw.strip()

    end = raw.find("\n---", 3)
    if end < 0:
        return {}, raw.strip()

    frontmatter_raw = raw[3:end].strip()
    body = raw[end + 4 :].strip()
    return parse_frontmatter(frontmatter_raw), body


def parse_frontmatter(raw: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None

    for line in raw.splitlines():
        list_match = re.match(r"^\s+-\s+(.*)$", line)
        if list_match and current_key:
            current = data.get(current_key)
            if not isinstance(current, list):
                current = []
            current.append(clean_scalar(list_match.group(1)))
            data[current_key] = current
            continue

        key_match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not key_match:
            continue

        current_key = key_match.group(1)
        value = key_match.group(2).strip()
        data[current_key] = clean_scalar(value) if value else []

    return data


def clean_scalar(value: str) -> str:
    return value.strip().strip("\"'")


def list_value(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, str) and value:
        return [value]
    return []


def format_frontmatter(data: dict[str, Any]) -> str:
    lines = ["---"]
    for key in REQUIRED_FRONTMATTER:
        if key not in data:
            continue
        value = data[key]
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    for key in sorted(set(data) - set(REQUIRED_FRONTMATTER)):
        value = data[key]
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def render_page(frontmatter: dict[str, Any], body: str) -> str:
    return f"{format_frontmatter(frontmatter)}\n\n{body.strip()}\n"


def load_pages() -> list[WikiPage]:
    pages: list[WikiPage] = []
    for path in sorted(WIKI_DIR.rglob("*.md")):
        raw = read_text(path)
        frontmatter, body = parse_markdown(raw)
        pages.append(
            WikiPage(
                path=path,
                relative_path=path.relative_to(WIKI_DIR).as_posix(),
                frontmatter=frontmatter,
                body=body,
                raw=raw,
            )
        )
    return pages


def read_page(path: Path) -> WikiPage:
    raw = read_text(path)
    frontmatter, body = parse_markdown(raw)
    return WikiPage(
        path=path,
        relative_path=path.relative_to(WIKI_DIR).as_posix(),
        frontmatter=frontmatter,
        body=body,
        raw=raw,
    )


def update_page(path: Path, frontmatter: dict[str, Any], body: str) -> None:
    frontmatter["updated"] = today()
    write_text(path, render_page(frontmatter, body))


def extract_markdown_links(body: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", body)


def resolve_wiki_link(page_relative_path: str, href: str) -> str | None:
    if re.match(r"^(https?:|mailto:|#)", href):
        return None
    base = Path(page_relative_path).parent
    normalized = (base / href).as_posix()
    parts: list[str] = []
    for part in normalized.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
        else:
            parts.append(part)
    return "/".join(parts)


def search_markdown(query: str, limit: int = 5) -> list[tuple[WikiPage, int, str]]:
    terms = query_terms(query)
    if not terms:
        return []

    scored: list[tuple[WikiPage, int, str]] = []
    for page in load_pages():
        text = f"{page.title}\n{' '.join(page.sources)}\n{page.body}"
        lower = text.lower()
        score = 0
        for term in terms:
            if term in page.title.lower():
                score += 10
            elif term in lower:
                score += 1
        if score:
            scored.append((page, score, best_snippet(page.body, terms)))

    return sorted(scored, key=lambda item: (-item[1], item[0].title))[:limit]


def query_terms(query: str) -> list[str]:
    lower = query.lower()
    stopwords = {
        "a",
        "an",
        "and",
        "are",
        "for",
        "how",
        "is",
        "of",
        "the",
        "to",
        "what",
        "with",
    }
    terms = [
        term
        for term in re.findall(r"[a-z0-9.]+", lower)
        if term not in stopwords and (len(term) > 1 or term == "c")
    ]
    phrases = ["software 2.0", "nanogpt", "mingpt", "llm.c", "cs231n"]
    for phrase in phrases:
        if phrase in lower:
            terms.append(phrase)
    return list(dict.fromkeys(terms))


def best_snippet(body: str, terms: list[str]) -> str:
    paragraphs = [line.strip() for line in body.splitlines() if line.strip() and not line.startswith("#")]
    for paragraph in paragraphs:
        lower = paragraph.lower()
        if any(term in lower for term in terms):
            return paragraph[:420]
    return (paragraphs[0] if paragraphs else "").strip()[:420]


def append_log(kind: str, title: str, details: str) -> None:
    log_path = WIKI_DIR / "log.md"
    page = read_page(log_path)
    entry = f"## [{today()}] {kind} | {title}\n\n{details.strip()}\n"
    body = page.body.rstrip() + "\n\n" + entry
    update_page(log_path, page.frontmatter, body)


def source_id_from_path_or_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        stem = Path(parsed.path).stem or parsed.netloc
        return slugify(stem)
    return slugify(Path(value).stem)


def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        pass
    else:
        load_dotenv(ROOT / ".env", override=True)

    local_cognee = ROOT / ".cognee"
    os.environ.setdefault("DATA_ROOT_DIRECTORY", str(local_cognee / "data"))
    os.environ.setdefault("SYSTEM_ROOT_DIRECTORY", str(local_cognee / "system"))
    os.environ.setdefault("CACHE_ROOT_DIRECTORY", str(local_cognee / "cache"))
    os.environ.setdefault("COGNEE_LOGS_DIR", str(local_cognee / "logs"))
    # This project runs Cognee session memory locally; do not require Redis.
    os.environ["CACHING"] = "true"
    os.environ["CACHE_BACKEND"] = "fs"
    os.environ.setdefault("COGNEE_LOG_FILE", "false")
    os.environ.setdefault("COGNEE_CLI_MODE", "true")
    os.environ.setdefault("COGNEE_MINIMAL_LOGGING", "true")
    os.environ.setdefault("ENABLE_BACKEND_ACCESS_CONTROL", "false")
    os.environ.setdefault("REQUIRE_AUTHENTICATION", "false")
    for key in ("DATA_ROOT_DIRECTORY", "SYSTEM_ROOT_DIRECTORY", "CACHE_ROOT_DIRECTORY", "COGNEE_LOGS_DIR"):
        Path(os.environ[key]).mkdir(parents=True, exist_ok=True)
    (Path(os.environ["SYSTEM_ROOT_DIRECTORY"]) / "databases").mkdir(parents=True, exist_ok=True)


def write_session_event(session_id: str | None, event: dict[str, Any]) -> str:
    if not session_id:
        return "session event skipped: no session id"

    load_dotenv_if_available()
    payload = json.dumps({"time": now_iso(), **event}, ensure_ascii=False)
    cache_backend = os.getenv("CACHE_BACKEND", "fs")
    caching = os.getenv("CACHING", "true")

    try:
        event_dir = Path(os.environ["CACHE_ROOT_DIRECTORY"]) / f"{DEFAULT_DATASET}-session-events"
        event_dir.mkdir(parents=True, exist_ok=True)
        event_path = event_dir / f"{slugify(session_id)}.jsonl"
        with event_path.open("a", encoding="utf-8") as file:
            file.write(payload + "\n")
    except Exception as exc:
        return f"fs session event skipped: {exc}"

    return f"fs session event wrote: {event_path} (CACHING={caching}, CACHE_BACKEND={cache_backend})"


async def cognee_remember(
    content: str,
    dataset: str = DEFAULT_DATASET,
    session_id: str | None = None,
) -> str:
    load_dotenv_if_available()
    try:
        import cognee
    except Exception as exc:
        return f"cognee skipped: {exc}"

    setup_status = await ensure_cognee_setup()
    if setup_status:
        return setup_status

    kwargs: dict[str, Any] = {"dataset_name": dataset}
    if session_id:
        kwargs["session_id"] = session_id

    try:
        await cognee.remember(content, **kwargs)
    except TypeError:
        try:
            if session_id:
                await cognee.remember(content, session_id=session_id)
            else:
                await cognee.remember(content)
        except Exception as exc:
            return f"cognee skipped: {exc}"
    except Exception as exc:
        return f"cognee skipped: {exc}"

    return "cognee remembered"


async def cognee_remember_many(
    contents: list[str],
    dataset: str = DEFAULT_DATASET,
    session_id: str | None = None,
) -> str:
    if not contents:
        return "cognee remembered 0 items"

    load_dotenv_if_available()
    try:
        import cognee
    except Exception as exc:
        return f"cognee skipped: {exc}"

    setup_status = await ensure_cognee_setup()
    if setup_status:
        return setup_status

    remembered = 0
    failures: list[str] = []
    for index, content in enumerate(contents, start=1):
        kwargs: dict[str, Any] = {"dataset_name": dataset}
        if session_id:
            kwargs["session_id"] = session_id

        try:
            await cognee.remember(content, **kwargs)
            remembered += 1
        except TypeError:
            try:
                if session_id:
                    await cognee.remember(content, session_id=session_id)
                else:
                    await cognee.remember(content)
                remembered += 1
            except Exception as exc:
                failures.append(f"{index}: {exc}")
        except Exception as exc:
            failures.append(f"{index}: {exc}")

    if failures:
        return f"cognee remembered {remembered}/{len(contents)} items; failures: {'; '.join(failures[:3])}"
    return f"cognee remembered {remembered}/{len(contents)} items"


async def cognee_recall(
    query: str,
    dataset: str = DEFAULT_DATASET,
    session_id: str | None = None,
) -> tuple[str, list[str]]:
    load_dotenv_if_available()
    try:
        import cognee
    except Exception as exc:
        return f"cognee skipped: {exc}", []

    setup_status = await ensure_cognee_setup()
    if setup_status:
        return setup_status, []

    attempts = [
        {"dataset_name": dataset, "session_id": session_id},
        {"datasets": [dataset], "session_id": session_id},
        {"session_id": session_id},
        {},
    ]

    last_error = ""
    for kwargs in attempts:
        clean = {key: value for key, value in kwargs.items() if value is not None}
        try:
            result = await cognee.recall(query, **clean)
            return "cognee recalled", normalize_cognee_results(result)
        except TypeError as exc:
            last_error = str(exc)
            continue
        except Exception as exc:
            return f"cognee skipped: {exc}", []

    return f"cognee skipped: {last_error}", []


async def ensure_cognee_setup() -> str:
    try:
        from cognee.modules.engine.operations.setup import setup

        await setup()
    except Exception as exc:
        return f"cognee skipped during setup: {exc}"
    return ""


def normalize_cognee_results(result: Any) -> list[str]:
    if result is None:
        return []
    if isinstance(result, str):
        return [result]
    if isinstance(result, list):
        return [json.dumps(item, ensure_ascii=False, default=str) if not isinstance(item, str) else item for item in result]
    return [json.dumps(result, ensure_ascii=False, default=str)]


def run_async(coro: Any) -> Any:
    return asyncio.run(coro)
