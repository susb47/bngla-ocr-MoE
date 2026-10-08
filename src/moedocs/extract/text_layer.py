"""Extract text + bboxes from an existing PDF text layer (no OCR)."""

from __future__ import annotations

from pathlib import Path

import pymupdf as fitz

from .engines.base import OcrLine, OcrResult


def extract_text_layer(pdf_path: Path, page_index: int) -> OcrResult:
    """
    page_index is 0-based.
    Returns lines with normalized bounding boxes from the PDF text layer.
    """
    doc = fitz.open(pdf_path)
    try:
        page = doc[page_index]
        pw = page.rect.width or 1.0
        ph = page.rect.height or 1.0

        # "dict" gives blocks → lines → spans
        data = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        lines: list[OcrLine] = []
        confs: list[float] = []

        for block in data.get("blocks", []):
            if block.get("type") != 0:  # 0 = text
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = "".join(s.get("text", "") for s in spans).strip()
                if not text:
                    continue
                # bbox from line
                x0, y0, x1, y1 = line["bbox"]
                bbox = (x0 / pw, y0 / ph, x1 / pw, y1 / ph)
                # Text layer has no confidence; assume high
                conf = 0.95
                lines.append(OcrLine(text=text, conf=conf, bbox=bbox))
                confs.append(conf)

        full = "\n".join(l.text for l in lines)
        avg = sum(confs) / len(confs) if confs else 0.0
        return OcrResult(
            lines=lines,
            full_text=full,
            engine="text_layer",
            avg_conf=avg,
        )
    finally:
        doc.close()
