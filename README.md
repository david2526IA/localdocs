# LocalDocs

> A private, source-grounded search assistant for personal text documents.

[![CI](https://github.com/david2526IA/localdocs/actions/workflows/ci.yml/badge.svg)](https://github.com/david2526IA/localdocs/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Privacy](https://img.shields.io/badge/Privacy-local--first-0F766E)](#privacy-and-scope)
[![License](https://img.shields.io/badge/License-MIT-2563EB.svg)](LICENSE)

LocalDocs helps people find information in their own notes, policies, manuals and text files without uploading them to a third-party AI service. It indexes `.txt` and `.md` files in local SQLite, retrieves the strongest matching passages and always displays the source that supports a result.

## Why this project

Useful AI products need more than a chat box. They need a privacy boundary, predictable retrieval, traceable sources, a clear deployment story and a user experience that works when no external model is available. LocalDocs demonstrates those foundations with a deliberately dependency-light implementation.

It performs retrieval, not unsupported document summarisation: users see the passages their answer is based on and can verify them directly.

## Features

- Local SQLite index — no cloud database or API key.
- Deterministic word chunking with overlap.
- Transparent BM25-style ranking for Spanish and English text.
- Source names, passage numbers and relevance scores on every result.
- CLI for automation and a small web interface for everyday users.
- Optional FastAPI service, Docker image, unit tests and CI.

## Architecture

```text
Markdown / text files
        │
        ▼
  Local chunking + checksum de-duplication
        │
        ▼
SQLite document index ──► lexical retrieval ──► source-backed passages
        │
        └──────────────────────────────► local web UI / CLI / API
```

## Quick start

```bash
git clone https://github.com/david2526IA/localdocs.git
cd localdocs
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -e ".[dev]"
localdocs ingest path/to/manual.md
localdocs ask "What does the warranty cover?"
localdocs status
pytest -q
```

## Local web app

```bash
pip install -e ".[web]"
uvicorn localdocs.api:app --reload
```

Open `http://127.0.0.1:8000`. Upload a `.txt` or `.md` document, then search it. The default database is `localdocs.db` in the current folder and is ignored by Git.

```bash
docker build -t localdocs .
docker run --rm -p 8000:8000 -v "${PWD}:/app/data" localdocs
```

## Privacy and scope

LocalDocs is designed to keep the baseline workflow local. It does not send document contents to a remote LLM, does not make claims beyond its sources and does not replace professional advice. For sensitive files, use full-disk encryption, access controls and the organisation's approved information-handling practices.

## Roadmap

- [ ] PDF/DOCX extraction with explicit local-only settings
- [ ] Optional local-LLM answer synthesis with cited passages
- [ ] Semantic/hybrid retrieval benchmark
- [ ] Encrypted index option
- [ ] Desktop packaging and accessibility review

## License

MIT © 2026 David Falcon
