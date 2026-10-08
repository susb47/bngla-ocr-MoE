"""Turn OCR/text-layer lines into typed Block objects."""

from __future__ import annotations

from ..schema import Block, BlockType
from .engines.base import OcrLine, OcrResult


def _guess_type(text: str, bbox: tuple[float, float, float, float], page_height_ratio: float) -> BlockType:
    """Very lightweight heuristics – good enough for MVP."""
    stripped = text.strip()
    # Header / footer by vertical position
    y0, y1 = bbox[1], bbox[3]
    if y1 < 0.08:
        return BlockType.header
    if y0 > 0.92:
        return BlockType.footer

    # Short uppercase-ish or numbered → heading
    if len(stripped) < 80 and (
        stripped.isupper()
        or stripped[:3].isdigit()
        or stripped.startswith(("Chapter", "Section", "পরিচ্ছেদ", "অধ্যায়", "বিষয়"))
    ):
        return BlockType.heading

    # Bullet-like
    if stripped.startswith(("-", "*", "•", "●", "○", "১.", "২.", "৩.", "1.", "2.", "3.")):
        return BlockType.list

    return BlockType.paragraph


def lines_to_blocks(
    result: OcrResult,
    page: int,
    *,
    id_prefix: str = "",
) -> list[Block]:
    """Convert OcrResult lines into Block list for one page."""
    blocks: list[Block] = []
    for i, line in enumerate(result.lines):
        bid = f"{id_prefix}{page}-{i + 1}" if id_prefix else f"{page}-{i + 1}"
        btype = _guess_type(line.text, line.bbox, line.bbox[3] - line.bbox[1])
        flags: list[str] = []
        if line.conf < 0.6:
            flags.append("low-conf")
        blocks.append(
            Block(
                id=bid,
                page=page,
                bbox=line.bbox,
                type=btype,
                text=line.text,
                conf=line.conf,
                engine=result.engine,
                flags=flags,
            )
        )
    return blocks
