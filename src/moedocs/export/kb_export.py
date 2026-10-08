"""Export approved documents to the chatbot knowledge-base folder."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..config import settings
from ..schema import DocStatus
from ..store import store


def _front_matter(meta) -> str:
    """YAML front matter for KB ingest scripts."""
    lines = [
        "---",
        f"doc_id: {meta.doc_id}",
        f"title: {meta.title or meta.doc_id}",
        f"agency: {meta.agency}",
        f"status: {meta.status.value}",
        f"confidence: {meta.confidence:.3f}",
        f"page_count: {meta.page_count}",
        f"source: {meta.source_filename or ''}",
        f"url: {meta.url or ''}",
        f"sha256: {meta.sha256}",
        f"exported_at: {datetime.now(timezone.utc).isoformat()}",
        "---",
        "",
    ]
    return "\n".join(lines)


def export_document(doc_id: str, kb_dir: Path | None = None) -> Path:
    """
    Write one approved document as Markdown into the KB folder.
    Returns the path of the written file.
    """
    if not store.exists(doc_id):
        raise FileNotFoundError(doc_id)

    meta = store.load_meta(doc_id)
    if meta.status != DocStatus.approved:
        raise ValueError(
            f"{doc_id} status is '{meta.status.value}', must be 'approved' to export"
        )

    kb_dir = Path(kb_dir or settings.kb_export_dir or Path("export_kb"))
    kb_dir.mkdir(parents=True, exist_ok=True)

    md = store.load_markdown(doc_id)
    content = _front_matter(meta) + md

    out = kb_dir / f"{doc_id}.md"
    out.write_text(content, encoding="utf-8")
    return out


def export_all_approved(kb_dir: Path | None = None) -> list[Path]:
    """Export every approved document. Returns list of written paths."""
    paths: list[Path] = []
    for summary in store.list_documents(status=DocStatus.approved):
        paths.append(export_document(summary.doc_id, kb_dir=kb_dir))
    return paths