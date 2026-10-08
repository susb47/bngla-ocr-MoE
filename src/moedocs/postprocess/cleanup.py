"""Generic cleanup: header/footer dedup, dehyphenation, empty block removal."""

from __future__ import annotations

from ..schema import Block, BlockType


def remove_empty(blocks: list[Block]) -> list[Block]:
    return [b for b in blocks if b.text.strip()]


def dehyphenate(text: str) -> str:
    """Join words split by hyphen at line end: 'exam-\\nple' → 'example'."""
    import re
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def drop_repeated_headers_footers(blocks: list[Block], *, min_pages: int = 2) -> list[Block]:
    """
    If the same header/footer text appears on many pages, mark it and optionally drop.
    MVP: just flag them, keep the first occurrence.
    """
    from collections import Counter

    header_texts = [b.text.strip() for b in blocks if b.type == BlockType.header]
    footer_texts = [b.text.strip() for b in blocks if b.type == BlockType.footer]
    header_counts = Counter(header_texts)
    footer_counts = Counter(footer_texts)

    seen_headers: set[str] = set()
    seen_footers: set[str] = set()
    out: list[Block] = []

    for b in blocks:
        t = b.text.strip()
        if b.type == BlockType.header and header_counts[t] >= min_pages:
            if t in seen_headers:
                b.flags = list(set(b.flags) | {"repeated-header"})
                continue  # drop duplicates
            seen_headers.add(t)
        if b.type == BlockType.footer and footer_counts[t] >= min_pages:
            if t in seen_footers:
                b.flags = list(set(b.flags) | {"repeated-footer"})
                continue
            seen_footers.add(t)
        out.append(b)
    return out


def postprocess_blocks(blocks: list[Block]) -> list[Block]:
    from .bangla import clean_bangla

    cleaned: list[Block] = []
    for b in blocks:
        b.text = clean_bangla(b.text)
        b.text = dehyphenate(b.text)
        cleaned.append(b)
    cleaned = remove_empty(cleaned)
    cleaned = drop_repeated_headers_footers(cleaned)
    return cleaned
