"""Assemble blocks into document.md with <!-- b:ID --> anchors."""

from __future__ import annotations

from ..schema import Block, BlockType


def block_to_md(block: Block) -> str:
    anchor = f"<!-- b:{block.id} -->"
    t = block.text.strip()
    if not t:
        return ""

    if block.type == BlockType.heading:
        # Choose level by length heuristic
        level = 1 if len(t) < 40 else 2
        return f"{anchor}\n{'#' * level} {t}\n"
    if block.type == BlockType.list:
        return f"{anchor}\n- {t}\n"
    if block.type == BlockType.table:
        # Placeholder – real tables come later
        return f"{anchor}\n\n{t}\n"
    if block.type in (BlockType.header, BlockType.footer):
        return f"{anchor}\n<!-- {block.type.value}: {t} -->\n"
    if block.type in (BlockType.stamp, BlockType.handwriting, BlockType.figure):
        return f"{anchor}\n<!-- {block.type.value}: {t[:60]} -->\n"
    # paragraph
    return f"{anchor}\n{t}\n"


def blocks_to_markdown(blocks: list[Block], *, title: str | None = None) -> str:
    parts: list[str] = []
    if title:
        parts.append(f"# {title}\n")
    current_page = None
    for b in sorted(blocks, key=lambda x: (x.page, x.bbox[1], x.bbox[0])):
        if b.page != current_page:
            current_page = b.page
            parts.append(f"\n<!-- page:{current_page} -->\n")
        md = block_to_md(b)
        if md:
            parts.append(md)
    return "\n".join(parts).strip() + "\n"
