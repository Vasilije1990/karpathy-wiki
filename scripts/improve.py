#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from wiki_common import (
    DEFAULT_DATASET,
    ROOT,
    WIKI_DIR,
    append_log,
    cognee_remember,
    read_page,
    run_async,
    slugify,
    update_page,
    write_session_event,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply feedback-driven wiki improvements.")
    parser.add_argument("--feedback", required=True, help="Path to feedback JSON")
    parser.add_argument("--apply", action="store_true", help="Apply changes instead of previewing")
    parser.add_argument("--session", default="karpathy-wiki-improve", help="Cognee session id")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Cognee dataset name")
    parser.add_argument("--graph", action="store_true", help="Also store the improvement record in Cognee graph")
    args = parser.parse_args()

    feedback_path = Path(args.feedback)
    data = json.loads(feedback_path.read_text(encoding="utf-8"))
    target_pages = [ROOT / path for path in data.get("target_pages", [])]

    note = build_improvement_note(data)
    missing = [path for path in target_pages if not path.exists()]
    if missing:
        for path in missing:
            print(f"missing target: {path.relative_to(ROOT)}")
        raise SystemExit(1)

    if not args.apply:
        print("Preview improvement note:")
        print(note)
        print()
        print("Target pages:")
        for path in target_pages:
            print(f"- {path.relative_to(ROOT)}")
        print("Run again with --apply to update pages.")
        return

    changed: list[str] = []
    marker = f"improvement:{slugify(data.get('query', 'feedback'))}"
    for path in target_pages:
        page = read_page(path)
        if marker in page.body:
            continue
        body = page.body.rstrip() + "\n\n" + note
        update_page(path, page.frontmatter, body)
        changed.append(path.relative_to(ROOT).as_posix())

    session_event_status = write_session_event(
        args.session,
        {
            "kind": "improve",
            "query": data.get("query"),
            "success_score": data.get("success_score"),
            "changed": changed,
        },
    )

    memory = {
        "kind": "karpathy_wiki_improvement",
        "feedback": data,
        "changed_pages": changed,
    }
    cognee_status = (
        run_async(cognee_remember(json.dumps(memory, ensure_ascii=False), args.dataset, None))
        if args.graph
        else "cognee graph skipped: pass --graph when LLM/network access is configured"
    )

    append_log(
        "improve",
        data.get("query", "feedback"),
        f"Applied feedback-driven improvement to {', '.join(changed) or 'no pages'}."
    )

    print(f"changed pages: {len(changed)}")
    for path in changed:
        print(f"- {path}")
    print(session_event_status)
    print(cognee_status)


def build_improvement_note(data: dict) -> str:
    query = data.get("query", "Unknown query")
    feedback = data.get("feedback", "No feedback provided.")
    score = data.get("success_score", "unknown")
    summary = data.get("improvement", {}).get("summary", "Improve this page using the feedback.")
    marker = f"improvement:{slugify(query)}"

    return f"""## Improvement Note

<!-- {marker} -->

Feedback query: `{query}`

Baseline score: `{score}`

Feedback: {feedback}

Durable update: {summary}
"""


if __name__ == "__main__":
    main()
