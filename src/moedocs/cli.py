"""Command-line interface for moe-docs."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.table import Table

from .config import settings
from .schema import DocStatus, Volatility
from .store import store

app = typer.Typer(
    name="moedocs",
    help="Bangla Document Pipeline – OCR/scrape → Markdown → review → training material",
    no_args_is_help=True,
)


# ---------------------------------------------------------------------------
# normalize
# ---------------------------------------------------------------------------

@app.command()
def normalize(
    source: Path = typer.Argument(..., help="Path to PDF / Office / image file"),
    doc_id: Optional[str] = typer.Option(None, "--id", help="Document ID (auto if omitted)"),
    agency: str = typer.Option("unknown", "--agency", "-a"),
    url: Optional[str] = typer.Option(None, "--url"),
    title: Optional[str] = typer.Option(None, "--title"),
    dpi: Optional[int] = typer.Option(None, "--dpi", help="Override view DPI"),
):
    """Convert a document into source.pdf + page images inside corpus/."""
    from .normalize import normalize_document

    source = source.expanduser().resolve()
    if not source.is_file():
        rprint(f"[red]File not found:[/red] {source}")
        raise typer.Exit(1)

    rprint(f"[cyan]Normalizing[/cyan] {source.name} …")
    meta = normalize_document(
        source,
        doc_id=doc_id,
        agency=agency,
        url=url,
        title=title,
        dpi=dpi,
    )
    rprint(f"[green]✓[/green] doc_id = [bold]{meta.doc_id}[/bold]")
    rprint(f"  pages     = {meta.page_count}")
    rprint(f"  sha256    = {meta.sha256[:16]}…")
    rprint(f"  corpus    = {store.doc_dir(meta.doc_id)}")


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

@app.command("list")
def list_docs(
    status: Optional[str] = typer.Option(None, "--status", "-s", help="pending|reviewed|approved|rejected"),
    agency: Optional[str] = typer.Option(None, "--agency", "-a"),
):
    """List documents in the corpus."""
    st = DocStatus(status) if status else None
    docs = store.list_documents(status=st, agency=agency)

    if not docs:
        rprint("[dim]No documents found.[/dim]")
        return

    table = Table(title="Corpus documents")
    table.add_column("doc_id", style="cyan")
    table.add_column("agency")
    table.add_column("status")
    table.add_column("pages", justify="right")
    table.add_column("conf", justify="right")
    table.add_column("title")

    for d in docs:
        table.add_row(
            d.doc_id,
            d.agency,
            d.status.value,
            str(d.page_count),
            f"{d.confidence:.0%}",
            (d.title or "")[:40],
        )
    rprint(table)


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------

@app.command()
def show(
    doc_id: str = typer.Argument(..., help="Document ID"),
):
    """Show metadata and page list for a document."""
    if not store.exists(doc_id):
        rprint(f"[red]Document not found:[/red] {doc_id}")
        raise typer.Exit(1)

    doc = store.load_document(doc_id)
    m = doc.meta
    rprint(f"[bold]{m.doc_id}[/bold]")
    rprint(f"  title      : {m.title}")
    rprint(f"  agency     : {m.agency}")
    rprint(f"  status     : {m.status.value}")
    rprint(f"  pages      : {m.page_count}")
    rprint(f"  confidence : {m.confidence:.1%}")
    rprint(f"  sha256     : {m.sha256}")
    rprint(f"  retrieved  : {m.retrieved_at.isoformat()}")
    rprint(f"  source     : {m.source_filename}")
    rprint(f"  path       : {store.doc_dir(doc_id)}")
    if doc.pages:
        rprint("  page images:")
        for p in doc.pages:
            rprint(f"    {p.page:4d}  {p.image_path}  ({p.width}×{p.height})" if p.width else f"    {p.page:4d}  {p.image_path}")


# ---------------------------------------------------------------------------
# status
# ---------------------------------------------------------------------------

@app.command()
def status(
    doc_id: str = typer.Argument(...),
    new_status: str = typer.Argument(..., help="pending|reviewed|approved|rejected"),
):
    """Change the status of a document."""
    if not store.exists(doc_id):
        rprint(f"[red]Document not found:[/red] {doc_id}")
        raise typer.Exit(1)
    st = DocStatus(new_status)
    meta = store.set_status(doc_id, st)
    rprint(f"[green]✓[/green] {doc_id} → [bold]{meta.status.value}[/bold]")


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

@app.command()
def delete(
    doc_id: str = typer.Argument(...),
    force: bool = typer.Option(False, "--force", "-f"),
):
    """Delete a document from the corpus."""
    if not store.exists(doc_id):
        rprint(f"[red]Document not found:[/red] {doc_id}")
        raise typer.Exit(1)
    if not force:
        confirm = typer.confirm(f"Delete {doc_id}?")
        if not confirm:
            raise typer.Abort()
    store.delete_doc(doc_id)
    rprint(f"[green]✓[/green] deleted {doc_id}")


# ---------------------------------------------------------------------------
# info
# ---------------------------------------------------------------------------

@app.command()
def info():
    """Show current configuration."""
    rprint(f"corpus_dir   : {settings.corpus_dir.resolve()}")
    rprint(f"sources_file : {settings.sources_file}")
    rprint(f"ocr_engine   : {settings.ocr_engine}")
    rprint(f"view_dpi     : {settings.view_dpi}")
    rprint(f"ocr_dpi      : {settings.ocr_dpi}")
    rprint(f"api_port     : {settings.api_port}")




# ---------------------------------------------------------------------------
# extract
# ---------------------------------------------------------------------------

@app.command()
def extract(
    doc_id: str = typer.Argument(..., help="Document ID already in corpus"),
    force_ocr: bool = typer.Option(False, "--force-ocr", help="Always run OCR"),
):
    """Triage + extract blocks (text layer or Tesseract) → blocks.json."""
    from .extract import extract_document

    if not store.exists(doc_id):
        rprint(f"[red]Document not found:[/red] {doc_id}")
        raise typer.Exit(1)

    rprint(f"[cyan]Extracting[/cyan] {doc_id} …")
    blocks = extract_document(doc_id, force_ocr=force_ocr)
    rprint(f"[green]✓[/green] {len(blocks)} blocks written to blocks.json")


# ---------------------------------------------------------------------------
# assemble
# ---------------------------------------------------------------------------

@app.command()
def assemble(
    doc_id: str = typer.Argument(...),
):
    """Postprocess blocks and build document.md with anchors."""
    from .assemble import assemble_document

    if not store.exists(doc_id):
        rprint(f"[red]Document not found:[/red] {doc_id}")
        raise typer.Exit(1)

    rprint(f"[cyan]Assembling[/cyan] {doc_id} …")
    md = assemble_document(doc_id)
    meta = store.load_meta(doc_id)
    rprint(f"[green]✓[/green] document.md written  confidence={meta.confidence:.1%}")
    rprint(f"  preview (first 300 chars):")
    rprint(f"  [dim]{md[:300]}…[/dim]" if len(md) > 300 else f"  [dim]{md}[/dim]")


# ---------------------------------------------------------------------------
# pipeline (normalize → extract → assemble)
# ---------------------------------------------------------------------------

@app.command()
def pipeline(
    source: Path = typer.Argument(..., help="Path to PDF / Office / image"),
    doc_id: Optional[str] = typer.Option(None, "--id"),
    agency: str = typer.Option("unknown", "--agency", "-a"),
    force_ocr: bool = typer.Option(False, "--force-ocr"),
):
    """Full MVP pipeline: normalize → extract → assemble."""
    from .normalize import normalize_document
    from .extract import extract_document
    from .assemble import assemble_document

    source = source.expanduser().resolve()
    if not source.is_file():
        rprint(f"[red]File not found:[/red] {source}")
        raise typer.Exit(1)

    rprint(f"[bold cyan]1/3 Normalize[/bold cyan] {source.name}")
    meta = normalize_document(source, doc_id=doc_id, agency=agency)
    doc_id = meta.doc_id
    rprint(f"  → {doc_id}  ({meta.page_count} pages)")

    rprint(f"[bold cyan]2/3 Extract[/bold cyan]")
    blocks = extract_document(doc_id, force_ocr=force_ocr)
    rprint(f"  → {len(blocks)} blocks")

    rprint(f"[bold cyan]3/3 Assemble[/bold cyan]")
    md = assemble_document(doc_id)
    meta = store.load_meta(doc_id)
    rprint(f"[green]✓ Done[/green]  confidence={meta.confidence:.1%}")
    rprint(f"  corpus/{doc_id}/document.md")
    rprint(f"  corpus/{doc_id}/blocks.json")

# ---------------------------------------------------------------------------
# serve (Review API)
# ---------------------------------------------------------------------------

@app.command()
def serve(
    host: str = typer.Option(None, "--host", help="Bind host"),
    port: int = typer.Option(None, "--port", help="Bind port"),
    reload: bool = typer.Option(True, "--reload/--no-reload"),
):
    """Start the Review API (FastAPI) for the web UI."""
    import uvicorn
    from .config import settings

    h = host or settings.api_host
    p = port or settings.api_port
    rprint(f"[cyan]Review API[/cyan] http://{h}:{p}")
    rprint(f"  corpus = {settings.corpus_dir.resolve()}")
    rprint("  UI: cd src/moedocs/review/web && npm run dev")
    uvicorn.run(
        "moedocs.review.api.main:app",
        host=h,
        port=p,
        reload=reload,
    )

# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------

@app.command("export")
def export_cmd(
    doc_id: Optional[str] = typer.Argument(None, help="Document ID (omit = all approved)"),
    kb_dir: Optional[Path] = typer.Option(None, "--kb-dir", help="Output folder"),
):
    """Export approved Markdown to the KB folder (for the chatbot)."""
    from .export import export_document, export_all_approved
    from .config import settings

    out_dir = kb_dir or settings.kb_export_dir or Path("export_kb")

    if doc_id:
        if not store.exists(doc_id):
            rprint(f"[red]Document not found:[/red] {doc_id}")
            raise typer.Exit(1)
        path = export_document(doc_id, kb_dir=out_dir)
        rprint(f"[green]✓[/green] exported {path}")
    else:
        paths = export_all_approved(kb_dir=out_dir)
        if not paths:
            rprint("[dim]No approved documents to export.[/dim]")
            return
        rprint(f"[green]✓[/green] exported {len(paths)} file(s) → {out_dir}")
        for p in paths:
            rprint(f"  {p}")

if __name__ == "__main__":
    app()
