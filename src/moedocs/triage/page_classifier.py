"""Classify each page: clean_text | garbled_text | scanned | mixed."""

from __future__ import annotations

from pathlib import Path

import pymupdf as fitz

from ..schema import PageClass
from .bangla_text_quality import bangla_ratio, is_likely_garbled, latin_ratio


def classify_page(pdf_path: Path, page_index: int) -> PageClass:
    """
    page_index is 0-based.
    Heuristic:
      - almost no extractable text → scanned
      - text exists but looks garbled → garbled_text
      - good Unicode text covering most of the page → clean_text
      - otherwise → mixed
    """
    doc = fitz.open(pdf_path)
    try:
        page = doc[page_index]
        text = page.get_text("text") or ""
        text = text.strip()

        # Image coverage heuristic
        image_area = 0.0
        page_area = page.rect.width * page.rect.height or 1.0
        for img in page.get_images(full=True):
            # We don't have exact bbox easily without more work; count images
            image_area += 1
        has_images = image_area > 0

        if len(text) < 30:
            return PageClass.scanned

        if is_likely_garbled(text):
            return PageClass.garbled_text

        # Reasonable amount of real text
        br = bangla_ratio(text)
        lr = latin_ratio(text)
        if (br + lr) > 0.15 and len(text) > 80:
            if has_images and len(text) < 200:
                return PageClass.mixed
            return PageClass.clean_text

        if has_images:
            return PageClass.mixed
        return PageClass.scanned
    finally:
        doc.close()


def classify_document(pdf_path: Path) -> list[PageClass]:
    doc = fitz.open(pdf_path)
    try:
        return [classify_page(pdf_path, i) for i in range(len(doc))]
    finally:
        doc.close()
