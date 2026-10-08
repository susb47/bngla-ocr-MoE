"""Convert various input formats into a single source.pdf."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

import pymupdf as fitz


SUPPORTED_DIRECT = {".pdf"}
SUPPORTED_OFFICE = {".doc", ".docx", ".odt", ".rtf", ".xls", ".xlsx", ".ppt", ".pptx"}
SUPPORTED_IMAGES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _libreoffice_convert(src: Path, out_dir: Path) -> Path:
    """Use LibreOffice headless to convert Office docs → PDF."""
    cmd = [
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(out_dir),
        str(src),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice conversion failed:\n{result.stderr or result.stdout}"
        )
    pdf = out_dir / (src.stem + ".pdf")
    if not pdf.is_file():
        # LibreOffice sometimes changes the name slightly
        candidates = list(out_dir.glob("*.pdf"))
        if not candidates:
            raise RuntimeError("LibreOffice produced no PDF")
        pdf = candidates[0]
    return pdf


def _images_to_pdf(images: list[Path], dest: Path) -> None:
    """Wrap one or more images into a single PDF."""
    doc = fitz.open()
    for img_path in images:
        img = fitz.open(img_path)
        pdf_bytes = img.convert_to_pdf()
        img_pdf = fitz.open("pdf", pdf_bytes)
        doc.insert_pdf(img_pdf)
        img.close()
        img_pdf.close()
    doc.save(dest)
    doc.close()


def to_pdf(source: Path, dest_pdf: Path) -> str:
    """
    Convert *source* (any supported format) into *dest_pdf*.

    Returns the SHA-256 of the original source file.
    """
    source = source.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)

    dest_pdf = dest_pdf.resolve()
    dest_pdf.parent.mkdir(parents=True, exist_ok=True)

    suffix = source.suffix.lower()
    sha = file_sha256(source)

    if suffix in SUPPORTED_DIRECT:
        shutil.copy2(source, dest_pdf)
        return sha

    if suffix in SUPPORTED_IMAGES:
        _images_to_pdf([source], dest_pdf)
        return sha

    if suffix in SUPPORTED_OFFICE:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            converted = _libreoffice_convert(source, tmp_path)
            shutil.copy2(converted, dest_pdf)
        return sha

    raise ValueError(
        f"Unsupported file type: {suffix}. "
        f"Supported: {sorted(SUPPORTED_DIRECT | SUPPORTED_OFFICE | SUPPORTED_IMAGES)}"
    )
