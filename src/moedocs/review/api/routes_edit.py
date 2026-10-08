"""Block-level edit routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...schema import Block, BlockType
from ...store import store

router = APIRouter(tags=["edit"])


class BlockPatch(BaseModel):
    text: str | None = None
    type: BlockType | None = None
    flags: list[str] | None = None


@router.patch("/docs/{doc_id}/blocks/{block_id}")
def patch_block(doc_id: str, block_id: str, body: BlockPatch):
    if not store.exists(doc_id):
        raise HTTPException(404, f"Document not found: {doc_id}")

    blocks = store.load_blocks(doc_id)
    target: Block | None = None
    for b in blocks:
        if b.id == block_id:
            target = b
            break
    if target is None:
        raise HTTPException(404, f"Block not found: {block_id}")

    if body.text is not None:
        target.text = body.text
    if body.type is not None:
        target.type = body.type
    if body.flags is not None:
        target.flags = body.flags

    store.save_blocks(doc_id, blocks)
    return target.model_dump()