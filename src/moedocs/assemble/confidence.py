"""Document and page confidence scores for the review queue."""

from __future__ import annotations

from ..schema import Block


def page_confidence(blocks: list[Block], page: int) -> float:
    page_blocks = [b for b in blocks if b.page == page]
    if not page_blocks:
        return 0.0
    return sum(b.conf for b in page_blocks) / len(page_blocks)


def document_confidence(blocks: list[Block]) -> float:
    if not blocks:
        return 0.0
    return sum(b.conf for b in blocks) / len(blocks)


def low_conf_count(blocks: list[Block], threshold: float = 0.6) -> int:
    return sum(1 for b in blocks if b.conf < threshold)
