from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .store import LocalDocsStore

app = FastAPI(title="LocalDocs API", version="0.1.0")
DATABASE = Path("localdocs.db")


class SearchRequest(BaseModel):
    query: str
    limit: int = 5


def _store() -> LocalDocsStore:
    return LocalDocsStore(DATABASE)


@app.get("/")
def home() -> FileResponse:
    return FileResponse(Path(__file__).parent / "web" / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/status")
def status() -> dict[str, int]:
    store = _store()
    try:
        return store.summary()
    finally:
        store.close()


@app.post("/v1/documents")
async def ingest(upload: UploadFile = File(...)) -> dict[str, object]:
    name = upload.filename or "untitled.txt"
    if Path(name).suffix.lower() not in {".txt", ".md"}:
        raise HTTPException(status_code=415, detail="Only .txt and .md files are supported")
    text = (await upload.read()).decode("utf-8", errors="strict")
    store = _store()
    try:
        return store.ingest_text(name, text)
    finally:
        store.close()


@app.post("/v1/search")
def search(request: SearchRequest) -> dict[str, object]:
    store = _store()
    try:
        return {"query": request.query, "results": store.search(request.query, request.limit)}
    finally:
        store.close()
