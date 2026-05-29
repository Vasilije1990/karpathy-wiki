#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

from wiki_common import DEFAULT_DATASET, ROOT, now_iso, write_text


DEFAULT_OUTPUT = ROOT / "src" / "cognee-graph.json"
GRAPH_DB = ROOT / ".cognee" / "system" / "databases" / "cognee_db"


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Cognee's graph database for the static wiki UI.")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="Cognee dataset name")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="JSON output path")
    args = parser.parse_args()

    output_path = Path(args.output)
    graph = export_graph(args.dataset)
    write_text(output_path, json.dumps(graph, ensure_ascii=False, indent=2))

    print(f"exported Cognee graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
    print(f"dataset: {graph['dataset']}")
    print(f"output: {output_path.relative_to(ROOT)}")


def export_graph(dataset_name: str) -> dict[str, Any]:
    if not GRAPH_DB.exists():
        return empty_graph(dataset_name, f"Cognee graph database not found at {GRAPH_DB}")

    with sqlite3.connect(GRAPH_DB) as connection:
        connection.row_factory = sqlite3.Row
        dataset = connection.execute(
            "select id, name from datasets where name = ?",
            (dataset_name,),
        ).fetchone()
        if not dataset:
            return empty_graph(dataset_name, f"Cognee dataset `{dataset_name}` was not found")

        raw_nodes = connection.execute(
            """
            select id, slug, label, type, indexed_fields, attributes, created_at
            from nodes
            where dataset_id = ?
            order by type, label
            """,
            (dataset["id"],),
        ).fetchall()
        raw_edges = connection.execute(
            """
            select source_node_id, destination_node_id, relationship_name, label, attributes
            from edges
            where dataset_id = ?
            order by relationship_name
            """,
            (dataset["id"],),
        ).fetchall()

    nodes = [normalize_node(row) for row in raw_nodes]
    node_ids = {node["id"] for node in nodes}
    edges = [
        normalize_edge(row)
        for row in raw_edges
        if compact_id(row["source_node_id"]) in node_ids and compact_id(row["destination_node_id"]) in node_ids
    ]

    return {
        "kind": "cognee-graph-export",
        "dataset": dataset["name"],
        "datasetId": dataset["id"],
        "exportedAt": now_iso(),
        "source": str(GRAPH_DB.relative_to(ROOT)),
        "nodeCount": len(nodes),
        "edgeCount": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


def normalize_node(row: sqlite3.Row) -> dict[str, Any]:
    attributes = parse_json(row["attributes"])
    canonical_id = compact_id(attributes.get("id") or row["label"] or row["id"])
    label = attributes.get("name") or row["label"] or f"{row['type']} {canonical_id[:8]}"
    description = attributes.get("description") or attributes.get("text") or ""

    return {
        "id": canonical_id,
        "label": clean_label(label),
        "type": row["type"],
        "description": clean_description(description),
        "sourceTask": attributes.get("source_task") or "",
        "sourcePipeline": attributes.get("source_pipeline") or "",
        "sourceContentHash": attributes.get("source_content_hash") or "",
        "createdAt": row["created_at"],
    }


def normalize_edge(row: sqlite3.Row) -> dict[str, str]:
    return {
        "source": compact_id(row["source_node_id"]),
        "target": compact_id(row["destination_node_id"]),
        "label": clean_label(row["label"] or row["relationship_name"]),
        "relationship": clean_label(row["relationship_name"]),
    }


def parse_json(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def compact_id(value: Any) -> str:
    return str(value).replace("-", "").lower()


def clean_label(value: Any) -> str:
    return " ".join(str(value).split())[:180]


def clean_description(value: Any) -> str:
    return " ".join(str(value).split())[:420]


def empty_graph(dataset_name: str, reason: str) -> dict[str, Any]:
    return {
        "kind": "cognee-graph-export",
        "dataset": dataset_name,
        "datasetId": "",
        "exportedAt": now_iso(),
        "source": str(GRAPH_DB.relative_to(ROOT)),
        "nodeCount": 0,
        "edgeCount": 0,
        "nodes": [],
        "edges": [],
        "error": reason,
    }


if __name__ == "__main__":
    main()
