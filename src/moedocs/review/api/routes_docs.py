"""Document list / detail / status / markdown routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...schema import DocStatus, DocumentSummary
from ...store import store

router = APIRouter(tags=["docs"])


class StatusBody(BaseModel):
    status: DocStatus


class MarkdownBody(BaseModel):
    markdown: str


@router.get("/docs", response_model=list[DocumentSummary])
def list_docs(status: DocStatus | None = None, agency: str | None = None):
    return store.list_documents(status=status, agency=agency)


@router.get("/docs/{doc_id}")
def get_doc(doc_id: str):
    if not store.exists(doc_id):
        raise HTTPException(404, f"Document not found: {doc_id}")
    doc = store.load_document(doc_id)
    return {
        "meta": doc.meta.model_dump(mode="json"),
        "markdown": doc.markdown,
        "blocks": [b.model_dump() for b in doc.blocks],
        "page_count": doc.meta.page_count,
        "confidence": doc.meta.confidence,
        "original_markdown": doc.original_markdown,
    }


@router.put("/docs/{doc_id}/markdown")
def put_markdown(doc_id: str, body: MarkdownBody):
    if not store.exists(doc_id):
        raise HTTPException(404, f"Document not found: {doc_id}")
    store.save_markdown(doc_id, body.markdown)
    return {"markdown": body.markdown, "ok": True}


@router.post("/docs/{doc_id}/status")
def set_status(doc_id: str, body: StatusBody):
    if not store.exists(doc_id):
        raise HTTPException(404, f"Document not found: {doc_id}")

    current = store.load_meta(doc_id).status
    new = body.status

    # Simple allowed transitions
    allowed = {
        DocStatus.pending: {DocStatus.reviewed, DocStatus.rejected, DocStatus.approved},
        DocStatus.reviewed: {DocStatus.approved, DocStatus.rejected, DocStatus.pending},
        DocStatus.approved: {DocStatus.pending, DocStatus.reviewed},
        DocStatus.rejected: {DocStatus.pending, DocStatus.reviewed},
    }
    if new not in allowed.get(current, set()) and new != current:
        raise HTTPException(
            400,
            f"Cannot change status {current.value} → {new.value}",
        )

    meta = store.set_status(doc_id, new)
    return {"status": meta.status.value, "ok": True}


@router.get("/docs/{doc_id}/diff")
def get_diff(doc_id: str):
    if not store.exists(doc_id):
        raise HTTPException(404, f"Document not found: {doc_id}")
    return {
        "original": store.load_markdown(doc_id, original=True),
        "current": store.load_markdown(doc_id),
    }