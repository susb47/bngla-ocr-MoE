"""OCR quality metrics: CER, WER, and a simple conjunct error rate."""

from __future__ import annotations

import re
from dataclasses import dataclass


def _levenshtein(a: str, b: str) -> int:
    """Classic Levenshtein distance."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            ins = cur[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def cer(ref: str, hyp: str) -> float:
    """Character Error Rate = edit_distance / len(ref)."""
    ref = ref.strip()
    hyp = hyp.strip()
    if not ref:
        return 0.0 if not hyp else 1.0
    return _levenshtein(ref, hyp) / len(ref)


def _words(text: str) -> list[str]:
    return re.findall(r"\S+", text)


def wer(ref: str, hyp: str) -> float:
    """Word Error Rate."""
    rw = _words(ref)
    hw = _words(hyp)
    if not rw:
        return 0.0 if not hw else 1.0
    # Treat as sequence of tokens
    return _levenshtein("\0".join(rw), "\0".join(hw)) / len(rw)


def conjunct_error_rate(ref: str, hyp: str) -> float:
    """
    Fraction of hasanta (্) positions in ref that are missing or wrong in hyp.
    Simple proxy for Bangla conjunct quality.
    """
    HASANTA = "\u09cd"
    ref_positions = [i for i, c in enumerate(ref) if c == HASANTA]
    if not ref_positions:
        return 0.0
    # Count how many hasantas in ref appear in a window in hyp
    hyp_has = set(i for i, c in enumerate(hyp) if c == HASANTA)
    # Approximate: compare counts + local context
    if abs(len(ref_positions) - len(hyp_has)) / max(len(ref_positions), 1) > 0.5:
        return 1.0
    # Character-level around hasanta
    errors = 0
    for i in ref_positions:
        window = ref[max(0, i - 2) : i + 3]
        if window not in hyp:
            errors += 1
    return errors / len(ref_positions)


@dataclass
class Metrics:
    cer: float
    wer: float
    conjunct_er: float
    ref_len: int
    hyp_len: int

    def as_dict(self) -> dict:
        return {
            "cer": round(self.cer, 4),
            "wer": round(self.wer, 4),
            "conjunct_er": round(self.conjunct_er, 4),
            "ref_len": self.ref_len,
            "hyp_len": self.hyp_len,
        }


def compute_metrics(ref: str, hyp: str) -> Metrics:
    return Metrics(
        cer=cer(ref, hyp),
        wer=wer(ref, hyp),
        conjunct_er=conjunct_error_rate(ref, hyp),
        ref_len=len(ref),
        hyp_len=len(hyp),
    )
