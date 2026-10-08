"""Shared Pydantic models – single source of truth for Block, Meta, Document."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BlockType(str, Enum):
    heading = "heading"
    paragraph = "paragraph"
    list = "list"
    table = "table"
    figure = "figure"
    header = "header"
    footer = "footer"
    stamp = "stamp"
    handwriting = "handwriting"


class DocStatus(str, Enum):
    pending = "pending"
    reviewed = "reviewed"
    approved = "approved"
    rejected = "rejected"


class Volatility(str, Enum):
    stable = "stable"
    semi = "semi"
    volatile = "volatile"


class PageClass(str, Enum):
    """Result of the triage step."""
    clean_text = "clean_text"
    garbled_text = "garbled_text"
    scanned = "scanned"
    mixed = "mixed"


# ---------------------------------------------------------------------------
# Core models
# ---------------------------------------------------------------------------

class Block(BaseModel):
    id: str
    page: int
    bbox: tuple[float, float, float, float] = Field(
        description="(x0, y0, x1, y1) – prefer normalized 0-1"
    )
    type: BlockType = BlockType.paragraph
    text: str = ""
    conf: float = Field(default=1.0, ge=0.0, le=1.0)
    engine: str = "unknown"
    flags: list[str] = Field(default_factory=list)


class Meta(BaseModel):
    doc_id: str
    url: str | None = None
    agency: str = "unknown"
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    sha256: str = ""
    as_of: date | None = None
    volatility: Volatility = Volatility.semi
    status: DocStatus = DocStatus.pending
    page_count: int = 0
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    title: str | None = None
    source_filename: str | None = None


class PageInfo(BaseModel):
    page: int
    image_path: str          # relative to corpus/<doc_id>/
    width: int
    height: int
    page_class: PageClass | None = None
    blocks: list[Block] = Field(default_factory=list)


class Document(BaseModel):
    """In-memory representation of everything we know about a document."""
    meta: Meta
    blocks: list[Block] = Field(default_factory=list)
    markdown: str = ""
    original_markdown: str | None = None  # raw OCR before human edits
    pages: list[PageInfo] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Lightweight list item (for the review queue)
# ---------------------------------------------------------------------------

class DocumentSummary(BaseModel):
    doc_id: str
    agency: str
    status: DocStatus
    page_count: int
    confidence: float
    title: str | None = None
    retrieved_at: datetime
