"""PII masking for export (stub – expand in Milestone 9)."""

from __future__ import annotations

import re

# Very light patterns for MVP
PHONE_RE = re.compile(r"\b(?:\+?88)?01[3-9]\d{8}\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


def mask_pii(text: str) -> str:
    text = PHONE_RE.sub("[PHONE]", text)
    text = EMAIL_RE.sub("[EMAIL]", text)
    return text
