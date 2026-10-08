"""Tesseract OCR engine (primary for Milestone 3+)."""

from __future__ import annotations

import os
from pathlib import Path

from .base import BaseEngine, OcrLine, OcrResult


def _configure_tesseract_cmd() -> None:
    """On Windows, point pytesseract at tesseract.exe if not on PATH."""
    import pytesseract

    # 1) Explicit env var wins
    env_cmd = os.environ.get("TESSERACT_CMD")
    if env_cmd and os.path.isfile(env_cmd):
        pytesseract.pytesseract.tesseract_cmd = env_cmd
        return

    # 2) Common Windows install path
    win_default = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.isfile(win_default):
        pytesseract.pytesseract.tesseract_cmd = win_default


class TesseractEngine(BaseEngine):
    name = "tesseract"

    def __init__(self, lang: str = "ben+eng"):
        self.lang = lang
        try:
            import pytesseract  # noqa: F401
            from PIL import Image  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "pytesseract and Pillow are required. "
                "Install with: pip install pytesseract pillow "
                "and ensure tesseract-ocr + ben language pack are installed."
            ) from e
        _configure_tesseract_cmd()

    def run(self, image_path: Path, *, lang: str | None = None) -> OcrResult:
        import pytesseract
        from PIL import Image

        lang = lang or self.lang
        img = Image.open(image_path)
        w, h = img.size

        data = pytesseract.image_to_data(
            img, lang=lang, output_type=pytesseract.Output.DICT
        )

        lines_map: dict[tuple[int, int], list[dict]] = {}
        n = len(data["text"])
        for i in range(n):
            text = (data["text"][i] or "").strip()
            conf_raw = int(data["conf"][i])
            if not text or conf_raw < 0:
                continue
            key = (data["block_num"][i], data["line_num"][i])
            lines_map.setdefault(key, []).append(
                {
                    "text": text,
                    "conf": conf_raw / 100.0,
                    "left": data["left"][i],
                    "top": data["top"][i],
                    "width": data["width"][i],
                    "height": data["height"][i],
                }
            )

        lines: list[OcrLine] = []
        confs: list[float] = []
        for key in sorted(lines_map.keys()):
            words = lines_map[key]
            text = " ".join(w["text"] for w in words)
            avg = sum(w["conf"] for w in words) / len(words)
            x0 = min(w["left"] for w in words) / w
            y0 = min(w["top"] for w in words) / h
            x1 = max(w["left"] + w["width"] for w in words) / w
            y1 = max(w["top"] + w["height"] for w in words) / h
            lines.append(OcrLine(text=text, conf=avg, bbox=(x0, y0, x1, y1)))
            confs.append(avg)

        full = "\n".join(l.text for l in lines)
        avg_conf = sum(confs) / len(confs) if confs else 0.0

        return OcrResult(
            lines=lines,
            full_text=full,
            engine=self.name,
            avg_conf=avg_conf,
        )


def get_engine(lang: str = "ben+eng") -> TesseractEngine:
    return TesseractEngine(lang=lang)