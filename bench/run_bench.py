#!/usr/bin/env python3
"""
Run OCR engines against gold pages and report CER / WER / conjunct ER.

Gold layout:
  bench/gold/
    <page_id>.png          # page image
    <page_id>.txt          # ground-truth text (UTF-8)

Usage:
  PYTHONPATH=src python bench/run_bench.py
  PYTHONPATH=src python bench/run_bench.py --engine tesseract
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running from repo root
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from metrics import compute_metrics  # noqa: E402


def load_gold(gold_dir: Path) -> list[tuple[str, Path, str]]:
    pages = []
    for txt in sorted(gold_dir.glob("*.txt")):
        img = txt.with_suffix(".png")
        if not img.is_file():
            img = txt.with_suffix(".jpg")
        if not img.is_file():
            print(f"  skip {txt.name}: no matching image")
            continue
        ref = txt.read_text(encoding="utf-8")
        pages.append((txt.stem, img, ref))
    return pages


def run_tesseract(image: Path, lang: str = "ben+eng") -> str:
    try:
        from moedocs.extract.engines.tesseract import TesseractEngine
    except ImportError:
        # Fallback if package not installed
        import pytesseract
        from PIL import Image
        return pytesseract.image_to_string(Image.open(image), lang=lang)

    engine = TesseractEngine(lang=lang)
    result = engine.run(image, lang=lang)
    return result.full_text


def main():
    parser = argparse.ArgumentParser(description="OCR benchmark on gold pages")
    parser.add_argument(
        "--gold",
        type=Path,
        default=ROOT / "bench" / "gold",
        help="Directory with .png + .txt gold pairs",
    )
    parser.add_argument("--engine", default="tesseract", choices=["tesseract"])
    parser.add_argument("--lang", default="ben+eng")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    pages = load_gold(args.gold)
    if not pages:
        print(f"No gold pages found in {args.gold}")
        print("Add pairs: <id>.png + <id>.txt")
        # Create a tiny placeholder note
        args.gold.mkdir(parents=True, exist_ok=True)
        readme = args.gold / "README.md"
        if not readme.is_file():
            readme.write_text(
                "# Gold pages\n\n"
                "Place hand-corrected pairs here:\n"
                "- `page001.png` – page image\n"
                "- `page001.txt` – ground-truth UTF-8 text\n",
                encoding="utf-8",
            )
        sys.exit(1)

    results = []
    print(f"Engine: {args.engine}  lang={args.lang}  pages={len(pages)}\n")
    print(f"{'page':<20} {'CER':>8} {'WER':>8} {'ConjER':>8}")
    print("-" * 50)

    for page_id, img, ref in pages:
        if args.engine == "tesseract":
            hyp = run_tesseract(img, lang=args.lang)
        else:
            hyp = ""
        m = compute_metrics(ref, hyp)
        results.append({"page": page_id, **m.as_dict()})
        print(f"{page_id:<20} {m.cer:8.3f} {m.wer:8.3f} {m.conjunct_er:8.3f}")

    # Aggregate
    if results:
        avg_cer = sum(r["cer"] for r in results) / len(results)
        avg_wer = sum(r["wer"] for r in results) / len(results)
        avg_cj = sum(r["conjunct_er"] for r in results) / len(results)
        print("-" * 50)
        print(f"{'AVERAGE':<20} {avg_cer:8.3f} {avg_wer:8.3f} {avg_cj:8.3f}")
        if args.json:
            print(json.dumps({"pages": results, "avg": {"cer": avg_cer, "wer": avg_wer, "conjunct_er": avg_cj}}, indent=2))


if __name__ == "__main__":
    main()
