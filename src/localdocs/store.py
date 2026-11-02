"""SQLite-backed local document store with source-preserving retrieval."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .chunking import chunk_text
from .retrieval import rank


class LocalDocsStore:
    def __init__(self, database_path: str | Path = "localdocs.db") -> None:
        self.connection = sqlite3.connect(database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents (
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              checksum TEXT NOT NULL UNIQUE,
              ingested_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS chunks (
              id INTEGER PRIMARY KEY,
              document_id INTEGER NOT NULL REFERENCES documents(id),
              ordinal INTEGER NOT NULL,
              content TEXT NOT NULL,
              UNIQUE(document_id, ordinal)
            );
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def ingest_text(self, name: str, text: str) -> dict[str, object]:
        content = text.strip()
        if not content:
            raise ValueError("A document cannot be empty")
        checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
        existing = self.connection.execute("SELECT id FROM documents WHERE checksum = ?", (checksum,)).fetchone()
        if existing:
            return {"status": "unchanged", "document_id": existing["id"], "chunks": 0}
        chunks = chunk_text(content)
        cursor = self.connection.execute(
            "INSERT INTO documents(name, checksum, ingested_at) VALUES (?, ?, ?)",
            (name, checksum, datetime.now(timezone.utc).isoformat()),
        )
        document_id = cursor.lastrowid
        self.connection.executemany(
            "INSERT INTO chunks(document_id, ordinal, content) VALUES (?, ?, ?)",
            [(document_id, ordinal, chunk) for ordinal, chunk in enumerate(chunks)],
        )
        self.connection.commit()
        return {"status": "indexed", "document_id": document_id, "chunks": len(chunks)}

    def ingest_file(self, path: str | Path) -> dict[str, object]:
        source = Path(path)
        if source.suffix.lower() not in {".txt", ".md"}:
            raise ValueError("Only .txt and .md files are supported in the local baseline")
        return self.ingest_text(source.name, source.read_text(encoding="utf-8"))

    def search(self, query: str, limit: int = 5) -> list[dict[str, object]]:
        rows = self.connection.execute(
            """
            SELECT chunks.id, chunks.ordinal, chunks.content, documents.name
            FROM chunks JOIN documents ON chunks.document_id = documents.id
            """
        ).fetchall()
        return rank(query, [dict(row) for row in rows], limit=limit)

    def summary(self) -> dict[str, int]:
        documents = self.connection.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        chunks = self.connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        return {"documents": documents, "chunks": chunks}
