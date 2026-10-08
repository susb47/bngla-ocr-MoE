"""Abstract OCR engine interface – all engines implement this."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class OcrLine:
    text: str
    conf: float  # 0-1
    bbox: tuple[float, float, float, float]  # x0,y0,x1,y1 normalized 0-1


@dataclass
class OcrResult:
    lines: list[OcrLine] = field(default_factory=list)
    full_text: str = ""
    engine: str = "unknown"
    avg_conf: float = 0.0


class BaseEngine(ABC):
    name: str = "base"

    @abstractmethod
    def run(self, image_path: Path, *, lang: str | None = None) -> OcrResult:
        """Run OCR on a single page image and return structured lines."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
