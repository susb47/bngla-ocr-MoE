"""Filesystem + JSON persistence for the corpus/ directory.

Layout for each document:
    corpus/<doc_id>/
        meta.json
        source.pdf          (or original file converted to PDF)
        pages/
            0001.png
            0002.png
            ...
        blocks.json         (list of Block)
        document.md         (assembled Markdown with anchors)
        original.md         (optional – raw OCR before edits)
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from .config import settings
from .schema import (
    Block,
    DocStatus,
    Document,
    DocumentSummary,
    Meta,
    PageInfo,
)


class Store:
    def __init__(self, corpus_dir: Path | None = None):
        self.root = Path(corpus_dir or settings.corpus_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def doc_dir(self, doc_id: str) -> Path:
        return self.root / doc_id

    def meta_path(self, doc_id: str) -> Path:
        return self.doc_dir(doc_id) / "meta.json"

    def source_pdf_path(self, doc_id: str) -> Path:
        return self.doc_dir(doc_id) / "source.pdf"

    def pages_dir(self, doc_id: str) -> Path:
        return self.doc_dir(doc_id) / "pages"

    def page_image_path(self, doc_id: str, page: int) -> Path:
        return self.pages_dir(doc_id) / f"{page:04d}.png"

    def blocks_path(self, doc_id: str) -> Path:
        return self.doc_dir(doc_id) / "blocks.json"

    def markdown_path(self, doc_id: str) -> Path:
        return self.doc_dir(doc_id) / "document.md"

    def original_md_path(self, doc_id: str) -> Path:
        return self.doc_dir(doc_id) / "original.md"

    # ------------------------------------------------------------------
    # Create / ensure
    # ------------------------------------------------------------------

    def create_doc(self, meta: Meta) -> Path:
        """Create the directory skeleton for a new document."""
        d = self.doc_dir(meta.doc_id)
        d.mkdir(parents=True, exist_ok=True)
        self.pages_dir(meta.doc_id).mkdir(exist_ok=True)
        self.save_meta(meta)
        return d

    def exists(self, doc_id: str) -> bool:
        return self.meta_path(doc_id).is_file()

    # ------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------

    def save_meta(self, meta: Meta) -> None:
        path = self.meta_path(meta.doc_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(meta.model_dump_json(indent=2), encoding="utf-8")

    def load_meta(self, doc_id: str) -> Meta:
        data = json.loads(self.meta_path(doc_id).read_text(encoding="utf-8"))
        return Meta.model_validate(data)

    # ------------------------------------------------------------------
    # Blocks
    # ------------------------------------------------------------------

    def save_blocks(self, doc_id: str, blocks: list[Block]) -> None:
        path = self.blocks_path(doc_id)
        payload = [b.model_dump() for b in blocks]
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def load_blocks(self, doc_id: str) -> list[Block]:
        path = self.blocks_path(doc_id)
        if not path.is_file():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return [Block.model_validate(item) for item in data]

    # ------------------------------------------------------------------
    # Markdown
    # ------------------------------------------------------------------

    def save_markdown(self, doc_id: str, markdown: str, *, original: bool = False) -> None:
        path = self.original_md_path(doc_id) if original else self.markdown_path(doc_id)
        path.write_text(markdown, encoding="utf-8")

    def load_markdown(self, doc_id: str, *, original: bool = False) -> str:
        path = self.original_md_path(doc_id) if original else self.markdown_path(doc_id)
        if not path.is_file():
            return ""
        return path.read_text(encoding="utf-8")

    # ------------------------------------------------------------------
    # Full document
    # ------------------------------------------------------------------

    def load_document(self, doc_id: str) -> Document:
        meta = self.load_meta(doc_id)
        blocks = self.load_blocks(doc_id)
        markdown = self.load_markdown(doc_id)
        original = self.load_markdown(doc_id, original=True) or None

        pages: list[PageInfo] = []
        pages_dir = self.pages_dir(doc_id)
        if pages_dir.is_dir():
            for img in sorted(pages_dir.glob("*.png")):
                page_num = int(img.stem)
                # width/height are filled later by the API if needed
                pages.append(
                    PageInfo(
                        page=page_num,
                        image_path=str(img.relative_to(self.doc_dir(doc_id))),
                        width=0,
                        height=0,
                        blocks=[b for b in blocks if b.page == page_num],
                    )
                )

        return Document(
            meta=meta,
            blocks=blocks,
            markdown=markdown,
            original_markdown=original,
            pages=pages,
        )

    def list_documents(
        self,
        status: DocStatus | None = None,
        agency: str | None = None,
    ) -> list[DocumentSummary]:
        summaries: list[DocumentSummary] = []
        if not self.root.is_dir():
            return summaries

        for child in sorted(self.root.iterdir()):
            if not child.is_dir():
                continue
            meta_file = child / "meta.json"
            if not meta_file.is_file():
                continue
            try:
                meta = self.load_meta(child.name)
            except Exception:
                continue
            if status and meta.status != status:
                continue
            if agency and meta.agency != agency:
                continue
            summaries.append(
                DocumentSummary(
                    doc_id=meta.doc_id,
                    agency=meta.agency,
                    status=meta.status,
                    page_count=meta.page_count,
                    confidence=meta.confidence,
                    title=meta.title,
                    retrieved_at=meta.retrieved_at,
                )
            )
        return summaries

    # ------------------------------------------------------------------
    # Status helper
    # ------------------------------------------------------------------

    def set_status(self, doc_id: str, status: DocStatus) -> Meta:
        meta = self.load_meta(doc_id)
        meta.status = status
        self.save_meta(meta)
        return meta

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def delete_doc(self, doc_id: str) -> None:
        d = self.doc_dir(doc_id)
        if d.is_dir():
            shutil.rmtree(d)


# Module-level convenience instance
store = Store()
