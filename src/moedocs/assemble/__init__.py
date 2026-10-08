"""Assemble cleaned blocks into document.md + confidence."""

from __future__ import annotations

from ..store import store
from ..postprocess import postprocess_blocks
from .to_markdown import blocks_to_markdown
from .confidence import document_confidence


def assemble_document(doc_id: str) -> str:
    """
    Load blocks, postprocess, write document.md + original.md, update meta.confidence.
    Returns the markdown string.
    """
    if not store.exists(doc_id):
        raise FileNotFoundError(doc_id)

    blocks = store.load_blocks(doc_id)
    blocks = postprocess_blocks(blocks)
    store.save_blocks(doc_id, blocks)

    meta = store.load_meta(doc_id)
    md = blocks_to_markdown(blocks, title=meta.title)
    conf = document_confidence(blocks)

    if not store.original_md_path(doc_id).is_file():
        store.save_markdown(doc_id, md, original=True)

    store.save_markdown(doc_id, md)
    meta.confidence = conf
    store.save_meta(meta)
    return md
