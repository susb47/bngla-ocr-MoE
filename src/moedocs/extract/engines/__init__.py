"""Pluggable OCR engines (Tesseract loaded only when needed)."""

from .base import BaseEngine, OcrLine, OcrResult

__all__ = ["BaseEngine", "OcrLine", "OcrResult", "TesseractEngine", "get_engine"]


def get_engine(lang: str = "ben+eng"):
    from .tesseract import TesseractEngine
    return TesseractEngine(lang=lang)


def __getattr__(name: str):
    if name == "TesseractEngine":
        from .tesseract import TesseractEngine
        return TesseractEngine
    raise AttributeError(name)