"""Extract text/blocks from a normalized document (text layer or OCR)."""

from __future__ import annotations

from pathlib import Path

from ..config import settings
from ..schema import Block, PageClass
from ..store import store
from ..triage import classify_page
from .engines.base import OcrResult
from .layout import lines_to_blocks
from .text_layer import extract_text_layer


def _try_ocr(page_image: Path, lang: str) -> OcrResult | None:
    """Run OCR if the engine is installed; otherwise return None."""
    try:
        from .engines import get_engine
    except ImportError:
        return None
    try:
        engine = get_engine(lang=lang)
        return engine.run(page_image, lang=lang)
    except ImportError:
        return None
    except Exception as e:
        print(f"  [warn] OCR failed ({e}); using text layer if available")
        return None


def extract_page(
    pdf_path: Path,
    page_image: Path,
    page_num: int,  # 1-based
    *,
    force_ocr: bool = False,
    engine_name: str | None = None,
) -> list[Block]:
    """
    Triage + extract a single page.
    Prefers PDF text layer; uses OCR only when needed and available.
    """
    page_index = page_num - 1
    page_class = classify_page(pdf_path, page_index)

    want_ocr = force_ocr or page_class in (
        PageClass.scanned,
        PageClass.garbled_text,
        PageClass.mixed,
    )

    result: OcrResult | None = None

    if want_ocr:
        result = _try_ocr(page_image, settings.tesseract_lang)

    if result is None:
        # Text layer (digital PDF) or fallback when OCR missing
        result = extract_text_layer(pdf_path, page_index)
        if len(result.full_text.strip()) < 20:
            # Almost empty – try OCR once more if possible
            ocr = _try_ocr(page_image, settings.tesseract_lang)
            if ocr is not None:
                result = ocr

    blocks = lines_to_blocks(result, page=page_num)
    if blocks and page_class != PageClass.clean_text:
        blocks[0].flags.append(f"page:{page_class.value}")
    return blocks


def extract_document(doc_id: str, *, force_ocr: bool = False) -> list[Block]:
    """Run extraction on every page. Saves blocks.json."""
    if not store.exists(doc_id):
        raise FileNotFoundError(f"Document not in corpus: {doc_id}")

    pdf_path = store.source_pdf_path(doc_id)
    meta = store.load_meta(doc_id)

    all_blocks: list[Block] = []
    for page_num in range(1, meta.page_count + 1):
        img = store.page_image_path(doc_id, page_num)
        if not img.is_file():
            continue
        blocks = extract_page(pdf_path, img, page_num, force_ocr=force_ocr)
        all_blocks.extend(blocks)

    store.save_blocks(doc_id, all_blocks)
    return all_blocks