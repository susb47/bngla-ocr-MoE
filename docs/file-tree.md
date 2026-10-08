# Full Project File Tree – moe-docs

```
moe-docs/
├── README.md
├── pyproject.toml
├── .env.example
├── sources.yml                          # agencies, URLs, cadence, volatility
│
├── docs/
│   ├── architecture.md                  # high-level system design (to be expanded)
│   ├── frontend.md                      # React UI architecture
│   ├── backend-connections.md           # API contract + how FE ↔ BE connect
│   ├── file-tree.md                     # this file
│   ├── schema.md                        # detailed Block / Meta contracts
│   └── runbook.md                       # ops / how to run each stage
│
├── src/moedocs/
│   ├── __init__.py
│   ├── config.py                        # settings, paths, engine registry
│   ├── schema.py                        # Pydantic models (Block, Meta, …)
│   ├── store.py                         # corpus/ filesystem abstraction
│   ├── cli.py                           # Typer CLI entrypoints
│   │
│   ├── acquire/
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   ├── crawler.py
│   │   ├── fetcher.py
│   │   └── html2md.py
│   │
│   ├── normalize/
│   │   ├── __init__.py
│   │   ├── to_pdf.py                    # LibreOffice / PyMuPDF conversion
│   │   └── render.py                    # page images at view + OCR DPI
│   │
│   ├── triage/
│   │   ├── __init__.py
│   │   ├── page_classifier.py
│   │   └── bangla_text_quality.py
│   │
│   ├── extract/
│   │   ├── __init__.py
│   │   ├── text_layer.py
│   │   ├── layout.py
│   │   ├── tables.py
│   │   ├── figures.py
│   │   └── engines/
│   │       ├── __init__.py
│   │       ├── base.py                  # abstract OCR engine interface
│   │       ├── tesseract.py
│   │       ├── surya.py
│   │       ├── paddle.py
│   │       ├── vlm.py
│   │       └── cloud.py
│   │
│   ├── postprocess/
│   │   ├── __init__.py
│   │   ├── bangla.py                    # NFC, conjunct repair, numerals
│   │   ├── cleanup.py                   # header/footer, dehyphenation
│   │   └── pii.py
│   │
│   ├── assemble/
│   │   ├── __init__.py
│   │   ├── to_markdown.py               # anchors + document.md
│   │   └── confidence.py
│   │
│   ├── review/
│   │   ├── api/                         # FastAPI backend
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── routes_docs.py
│   │   │   ├── routes_pages.py
│   │   │   └── routes_edit.py
│   │   │
│   │   └── web/                         # React frontend (this is fully scaffolded)
│   │       ├── package.json
│   │       ├── vite.config.ts
│   │       ├── tsconfig.json
│   │       ├── tsconfig.node.json
│   │       ├── index.html
│   │       ├── postcss.config.js
│   │       ├── tailwind.config.js
│   │       └── src/
│   │           ├── main.tsx
│   │           ├── App.tsx
│   │           ├── index.css
│   │           ├── vite-env.d.ts
│   │           ├── api/
│   │           │   └── client.ts
│   │           ├── types/
│   │           │   └── index.ts
│   │           ├── state/
│   │           │   ├── store.ts
│   │           │   └── sync.ts
│   │           └── components/
│   │               ├── QueueSidebar.tsx
│   │               ├── SplitLayout.tsx
│   │               ├── SourcePane.tsx
│   │               ├── BlockOverlay.tsx
│   │               ├── MarkdownEditor.tsx
│   │               ├── MarkdownPreview.tsx
│   │               ├── ConfidenceLegend.tsx
│   │               ├── DiffToggle.tsx
│   │               └── StatusBar.tsx
│   │
│   └── export/
│       ├── __init__.py
│       ├── kb_export.py
│       ├── sft_builder.py
│       └── refresh.py
│
├── bench/
│   ├── gold/                            # hand-corrected pages + ground truth
│   ├── metrics.py
│   └── run_bench.py
│
├── corpus/                              # gitignored – runtime data
│   └── <doc_id>/
│       ├── source.pdf
│       ├── pages/
│       │   ├── 0001.png
│       │   └── …
│       ├── blocks.json
│       ├── document.md
│       └── meta.json
│
└── tests/
    ├── test_schema.py
    ├── test_normalize.py
    └── …
```

---

## What is already created

| Path | Status |
|------|--------|
| Full directory skeleton | ✅ |
| Frontend (all files under `review/web/`) | ✅ complete |
| `docs/frontend.md` | ✅ |
| `docs/backend-connections.md` | ✅ |
| `docs/file-tree.md` | ✅ |

Backend Python modules (schema, store, normalize, FastAPI routes, etc.) are **not** yet implemented – they belong to Milestone 1 onward.
