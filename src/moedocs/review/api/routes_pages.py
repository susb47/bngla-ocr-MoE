"""Page image serving + page metadata."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ...store import store
from ...normalize.render import get_page_size

router = APIRouter(tags=["pages"])


@router.get("/docs/{doc_id}/pages/{page}")
def get_page(doc_id: str, page: int):
    if not store.exists(doc_id):
        raise HTTPException(404, f"Document not found: {doc_id}")

    img_path = store.page_image_path(doc_id, page)
    if not img_path.is_file():
        raise HTTPException(404, f"Page {page} not found")

    width, height = get_page_size(img_path)
    blocks = [b for b in store.load_blocks(doc_id) if b.page == page]

    return {
        "page": page,
        "image_url": f"/api/docs/{doc_id}/pages/{page}/image",
        "width": width,
        "height": height,
        "blocks": [b.model_dump() for b in blocks],
    }


@router.get("/docs/{doc_id}/pages/{page}/image")
def get_page_image(doc_id: str, page: int):
    if not store.exists(doc_id):
        raise HTTPException(404, f"Document not found: {doc_id}")

    img_path = store.page_image_path(doc_id, page)
    if not img_path.is_file():
        raise HTTPException(404, f"Page image {page} not found")

    return FileResponse(img_path, media_type="image/png")
