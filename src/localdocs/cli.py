from __future__ import annotations

import argparse
from pathlib import Path

from .store import LocalDocsStore


def main() -> None:
    parser = argparse.ArgumentParser(prog="localdocs")
    parser.add_argument("--db", default="localdocs.db", help="local SQLite database path")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="index a .txt or .md file")
    ingest.add_argument("file")
    ask = commands.add_parser("ask", help="retrieve source-backed passages")
    ask.add_argument("query")
    ask.add_argument("--limit", type=int, default=3)
    commands.add_parser("status", help="show local index statistics")
    args = parser.parse_args()
    store = LocalDocsStore(args.db)
    try:
        if args.command == "ingest":
            print(store.ingest_file(args.file))
        elif args.command == "status":
            print(store.summary())
        else:
            results = store.search(args.query, args.limit)
            if not results:
                print("No relevant local source found.")
            for item in results:
                print(f"\n[{item['name']} · passage {item['ordinal']} · score {item['score']}]\n{item['content']}")
    finally:
        store.close()


if __name__ == "__main__":
    main()
