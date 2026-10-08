"""Render each page of a PDF into PNG images."""

from __future__ import annotations

from pathlib import Path

import pymupdf as fitz
from PIL import Image

from ..config import settings


def render_pages(
    pdf_path: Path,
    pages_dir: Path,
    *,
    dpi: int | None = None,
    fmt: str = "png",
) -> list[dict]:
    """
    Render every page of *pdf_path* into *pages_dir*.

    Returns a list of dicts:
        [{"page": 1, "path": Path(...), "width": 1654, "height": 2339}, ...]
    """
    dpi = dpi or settings.view_dpi
    pages_dir.mkdir(parents=True, exist_ok=True)

    # Clear old images so we don't leave stale pages
    for old in pages_dir.glob(f"*.{fmt}"):
        old.unlink()

    doc = fitz.open(pdf_path)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    results: list[dict] = []
    for i in range(len(doc)):
        page = doc[i]
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        out_path = pages_dir / f"{i + 1:04d}.{fmt}"
        pix.save(str(out_path))

        results.append(
            {
                "page": i + 1,
                "path": out_path,
                "width": pix.width,
                "height": pix.height,
            }
        )
    doc.close()
    return results


def page_count(pdf_path: Path) -> int:
    doc = fitz.open(pdf_path)
    n = len(doc)
    doc.close()
    return n


def get_page_size(image_path: Path) -> tuple[int, int]:
    with Image.open(image_path) as im:
        return im.size  # (width, height)
