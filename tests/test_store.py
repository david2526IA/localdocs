from localdocs.chunking import chunk_text
from localdocs.store import LocalDocsStore


def test_chunking_retains_overlap() -> None:
    chunks = chunk_text(" ".join(str(number) for number in range(200)), size=100, overlap=20)
    assert len(chunks) == 3
    assert "80" in chunks[0]
    assert "80" in chunks[1]


def test_ingest_and_search_returns_source(tmp_path) -> None:
    store = LocalDocsStore(tmp_path / "docs.db")
    try:
        result = store.ingest_text("warranty.md", "The battery warranty covers manufacturing defects for two years.")
        assert result["status"] == "indexed"
        matches = store.search("How long is the battery warranty?")
        assert matches[0]["name"] == "warranty.md"
        assert "two years" in matches[0]["content"]
    finally:
        store.close()


def test_duplicate_content_is_not_indexed_twice(tmp_path) -> None:
    store = LocalDocsStore(tmp_path / "docs.db")
    try:
        store.ingest_text("first.md", "One local source with enough words to be indexed.")
        duplicate = store.ingest_text("second.md", "One local source with enough words to be indexed.")
        assert duplicate["status"] == "unchanged"
        assert store.summary()["documents"] == 1
    finally:
        store.close()
