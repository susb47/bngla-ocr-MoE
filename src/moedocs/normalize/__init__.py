"""Normalize any supported document into source.pdf + page images."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from ..schema import Meta, DocStatus, Volatility
from ..store import store
from .to_pdf import to_pdf, file_sha256
from .render import render_pages, page_count


def normalize_document(
    source: Path,
    *,
    doc_id: str | None = None,
    agency: str = "unknown",
    url: str | None = None,
    title: str | None = None,
    volatility: Volatility = Volatility.semi,
    dpi: int | None = None,
) -> Meta:
    """
    End-to-end normalize:

    1. Derive doc_id if not given
    2. Convert source to source.pdf
    3. Render page images
    4. Write meta.json

    Returns the Meta of the created/updated document.
    """
    source = Path(source).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)

    if doc_id is None:
        # Simple deterministic id from filename + short hash
        sha = file_sha256(source)[:10]
        stem = source.stem.replace(" ", "_")[:40]
        doc_id = f"{stem}-{sha}"

    meta = Meta(
        doc_id=doc_id,
        url=url,
        agency=agency,
        retrieved_at=datetime.utcnow(),
        sha256="",  # filled after conversion
        volatility=volatility,
        status=DocStatus.pending,
        title=title or source.stem,
        source_filename=source.name,
    )

    # Create directory skeleton
    store.create_doc(meta)

    # Convert to PDF
    pdf_path = store.source_pdf_path(doc_id)
    sha = to_pdf(source, pdf_path)
    meta.sha256 = sha

    # Render pages
    pages_dir = store.pages_dir(doc_id)
    page_infos = render_pages(pdf_path, pages_dir, dpi=dpi)
    meta.page_count = len(page_infos)

    store.save_meta(meta)
    return meta
