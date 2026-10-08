"""Bangla-specific text fixes: NFC, hasanta/joiner repair, numeral consistency."""

from __future__ import annotations

import re
import unicodedata

# Common broken sequences → correct Bangla
# (keep minimal for MVP; expand with real corpus later)
REPAIRS = [
    # Zero-width joiners / non-joiners cleanup around hasanta
    (re.compile(r"\u09cd\u200c"), "\u09cd"),   # hasanta + ZWNJ → hasanta
    (re.compile(r"\u200c\u09cd"), "\u09cd"),
    # Multiple spaces
    (re.compile(r"[ \t]+"), " "),
]

# Bangla digits → ASCII (optional, controlled by flag)
BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def repair_conjuncts(text: str) -> str:
    for pat, repl in REPAIRS:
        text = pat.sub(repl, text)
    return text


def normalize_numerals(text: str, *, to_ascii: bool = False) -> str:
    if to_ascii:
        return text.translate(BN_DIGITS)
    return text


def clean_bangla(text: str, *, ascii_numerals: bool = False) -> str:
    text = nfc(text)
    text = repair_conjuncts(text)
    text = normalize_numerals(text, to_ascii=ascii_numerals)
    text = text.strip()
    return text
