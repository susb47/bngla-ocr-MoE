"""Heuristics for Bangla text-layer quality (detect garbled / legacy fonts)."""

from __future__ import annotations

import re
import unicodedata

# Common Bangla Unicode range
BANGLA_RE = re.compile(r"[\u0980-\u09FF]")
# Basic Latin letters (suggests English or romanized)
LATIN_RE = re.compile(r"[A-Za-z]")
# Private-use / replacement chars often left by broken encodings
GARBLED_RE = re.compile(r"[\ufffd\u0000-\u0008\ue000-\uf8ff]")


def bangla_ratio(text: str) -> float:
    if not text:
        return 0.0
    bangla = len(BANGLA_RE.findall(text))
    return bangla / max(len(text), 1)


def latin_ratio(text: str) -> float:
    if not text:
        return 0.0
    return len(LATIN_RE.findall(text)) / max(len(text), 1)


def garbled_ratio(text: str) -> float:
    if not text:
        return 0.0
    return len(GARBLED_RE.findall(text)) / max(len(text), 1)


def has_bangla_conjuncts(text: str) -> bool:
    """Rough check: presence of hasanta (্) indicates real Bangla orthography."""
    return "\u09cd" in text  # U+09CD HASANTA


def is_likely_garbled(text: str, *, min_chars: int = 40) -> bool:
    """
    Return True if the text layer looks like a broken legacy-font encoding
    rather than proper Unicode Bangla.
    """
    if len(text.strip()) < min_chars:
        return False
    if garbled_ratio(text) > 0.05:
        return True
    # Lots of Latin but claims to be Bangla doc, and almost no real Bangla
    if bangla_ratio(text) < 0.02 and latin_ratio(text) > 0.3:
        # Could still be pure English – only flag if there are weird high bytes
        if any(ord(c) > 127 and not BANGLA_RE.match(c) for c in text[:500]):
            return True
    # Bangla chars present but no hasanta and very few independent vowels → suspicious
    if bangla_ratio(text) > 0.1 and not has_bangla_conjuncts(text):
        # Many legacy fonts map incorrectly; treat as soft signal
        return bangla_ratio(text) > 0.2 and len(text) > 200
    return False


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)
