"""Basic smoke tests for Milestone 1 (normalize + store)."""

from pathlib import Path

import pytest

from moedocs.normalize import normalize_document
from moedocs.store import Store
from moedocs.schema import DocStatus


FIXTURE = Path(__file__).parent / "fixtures" / "sample-circular.pdf"


@pytest.fixture
def tmp_store(tmp_path, monkeypatch):
    """Use a temporary corpus directory."""
    from moedocs import config
    monkeypatch.setattr(config.settings, "corpus_dir", tmp_path)
    return Store(corpus_dir=tmp_path)


def test_normalize_creates_pages(tmp_store, monkeypatch):
    from moedocs import store as store_mod
    monkeypatch.setattr(store_mod, "store", tmp_store)
    # also patch the store used inside normalize
    import moedocs.normalize as norm
    monkeypatch.setattr(norm, "store", tmp_store)

    meta = normalize_document(
        FIXTURE,
        doc_id="test-doc-001",
        agency="Test Agency",
        title="Test Circular",
    )

    assert meta.doc_id == "test-doc-001"
    assert meta.page_count == 3
    assert meta.status == DocStatus.pending
    assert meta.sha256
    assert tmp_store.exists("test-doc-001")
    assert tmp_store.source_pdf_path("test-doc-001").is_file()
    assert tmp_store.page_image_path("test-doc-001", 1).is_file()
    assert tmp_store.page_image_path("test-doc-001", 3).is_file()


def test_list_and_load(tmp_store, monkeypatch):
    from moedocs import store as store_mod
    monkeypatch.setattr(store_mod, "store", tmp_store)
    import moedocs.normalize as norm
    monkeypatch.setattr(norm, "store", tmp_store)

    normalize_document(FIXTURE, doc_id="list-test", agency="MoE")
    docs = tmp_store.list_documents()
    assert len(docs) == 1
    assert docs[0].doc_id == "list-test"

    doc = tmp_store.load_document("list-test")
    assert doc.meta.page_count == 3
    assert len(doc.pages) == 3
