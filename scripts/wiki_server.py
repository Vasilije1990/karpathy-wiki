#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import mimetypes
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from query import answer_question
from wiki_common import DEFAULT_DATASET, ROOT


class WikiRequestHandler(BaseHTTPRequestHandler):
    static_root = ROOT / "dist"

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self.write_json({"ok": True, "service": f"{DEFAULT_DATASET}-api"})
            return
        self.serve_static()

    def do_POST(self) -> None:
        if self.path != "/api/query":
            self.write_json({"error": "not found"}, status=404)
            return

        try:
            payload = self.read_json()
            question = str(payload.get("question", "")).strip()
            if not question:
                self.write_json({"error": "question is required"}, status=400)
                return

            result = answer_question(
                question=question,
                session=str(payload.get("session") or f"{DEFAULT_DATASET}-web"),
                dataset=str(payload.get("dataset") or DEFAULT_DATASET),
                use_cognee=bool(payload.get("cognee", True)),
                file_answer_enabled=bool(payload.get("fileAnswer", True)),
                reviewed=bool(payload.get("reviewed", True)),
            )
            self.write_json(
                {
                    "question": result.question,
                    "answer": result.answer,
                    "cogneeStatus": result.cognee_status,
                    "sessionEventStatus": result.session_event_status,
                    "filedPath": result.filed_path,
                    "evidence": [asdict(item) for item in result.evidence],
                }
            )
        except Exception as exc:
            self.write_json({"error": str(exc)}, status=500)

    def read_json(self) -> dict:
        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        if not body:
            return {}
        parsed = json.loads(body)
        return parsed if isinstance(parsed, dict) else {}

    def write_json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_cors_headers()
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def serve_static(self) -> None:
        request_path = unquote(self.path.split("?", 1)[0]).lstrip("/")
        relative_path = Path(request_path or "index.html")
        if relative_path.parts and relative_path.parts[0] == "api":
            self.write_json({"error": "not found"}, status=404)
            return

        path = (self.static_root / relative_path).resolve()
        if not str(path).startswith(str(self.static_root.resolve())):
            self.write_json({"error": "forbidden"}, status=403)
            return
        if not path.exists() or path.is_dir():
            path = self.static_root / "index.html"
        if not path.exists():
            self.write_json({"error": "dist not found; run npm run build"}, status=404)
            return

        data = path.read_bytes()
        self.send_response(200)
        self.send_cors_headers()
        self.send_header("content-type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_cors_headers(self) -> None:
        self.send_header("access-control-allow-origin", "*")
        self.send_header("access-control-allow-methods", "GET, POST, OPTIONS")
        self.send_header("access-control-allow-headers", "content-type")

    def log_message(self, format: str, *args) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the wiki frontend and live Cognee query API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--static-root", default=str(ROOT / "dist"))
    args = parser.parse_args()

    WikiRequestHandler.static_root = Path(args.static_root)
    server = ThreadingHTTPServer((args.host, args.port), WikiRequestHandler)
    print(f"Wiki API serving http://{args.host}:{args.port}")
    print(f"static root: {WikiRequestHandler.static_root}")
    server.serve_forever()


if __name__ == "__main__":
    main()
