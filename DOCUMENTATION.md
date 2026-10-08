# moe-docs — Complete Documentation

**Bangla Document Pipeline**  
OCR / scrape → Markdown → human review → knowledge base + training material

This is a **standalone project**. It does not live inside the chatbot repo; it only **exports** approved Markdown into the chatbot’s KB folder.

---

## Table of contents

1. [Goals and principles](#1-goals-and-principles)
2. [High-level architecture](#2-high-level-architecture)
3. [Project layout](#3-project-layout)
4. [Shared data contracts](#4-shared-data-contracts)
5. [Pipeline stages](#5-pipeline-stages)
6. [CLI reference](#6-cli-reference)
7. [Review API](#7-review-api)
8. [Frontend (Review UI)](#8-frontend-review-ui)
9. [Setup (Windows CMD)](#9-setup-windows-cmd)
10. [Runbook — day-to-day](#10-runbook--day-to-day)
11. [OCR notes](#11-ocr-notes)
12. [Export to chatbot KB](#12-export-to-chatbot-kb)
13. [Milestones status](#13-milestones-status)
14. [Configuration](#14-configuration)
15. [Git](#15-git)
16. [Troubleshooting](#16-troubleshooting)

---

## 1. Goals and principles

### Goal

Turn official Bangla documents (digital PDFs, Office files, scans, images) into **reviewed, traceable Markdown** that feeds:

- the chatbot **knowledge base**, and  
- optionally a **training / SFT** set.

### Principles

1. **Traceability** — every Markdown block points back to a page and bounding box (`<!-- b:ID -->`).
2. **Page-level decisions** — one PDF can mix clean text, garbled text, and scans; each page is handled on its own.
3. **Human gate** — only **approved** documents are exported.
4. **Pluggable OCR** — engines sit behind one interface; benchmark on your own gold pages.
5. **Separate repo** — this project owns the pipeline; the chatbot only consumes exported files.

---

## 2. High-level architecture

```text
sources.yml  →  acquire (later)
                    ↓
              normalize  →  source.pdf + pages/*.png
                    ↓
              triage     →  clean | garbled | scanned | mixed
                    ↓
              extract    →  text layer and/or OCR → blocks.json
                    ↓
              postprocess → Bangla cleanup, headers/footers
                    ↓
              assemble   →  document.md + confidence
                    ↓
              Review UI  →  human edit / approve / reject
                    ↓
              export     →  KB Markdown (+ SFT later)
```

**Backend:** Python 3.11+, FastAPI, PyMuPDF, optional Tesseract  
**Frontend:** React + Vite + CodeMirror + Zustand  
**Storage:** filesystem under `corpus/<doc_id>/`

---

## 3. Project layout

```text
moe-docs/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── sources.yml                 # agency crawl targets (Milestone 8)
│
├── docs/
│   ├── DOCUMENTATION.md        # this file
│   ├── runbook.md              # short Windows run steps
│   ├── frontend.md
│   ├── backend-connections.md
│   └── file-tree.md
│
├── src/moedocs/
│   ├── config.py               # settings from .env
│   ├── schema.py               # Block, Meta, Document, …
│   ├── store.py                # corpus read/write
│   ├── cli.py                  # moedocs CLI
│   │
│   ├── normalize/              # any file → PDF + page images
│   ├── triage/                 # page classification + Bangla quality
│   ├── extract/                # text layer + OCR + layout → blocks
│   │   └── engines/            # tesseract (pluggable)
│   ├── postprocess/            # Bangla NFC, cleanup, PII stub
│   ├── assemble/               # blocks → document.md + confidence
│   ├── export/                 # approved → KB Markdown
│   │
│   └── review/
│       ├── api/                # FastAPI
│       └── web/                # React review UI
│
├── bench/                      # OCR quality metrics + gold pages
├── corpus/                     # runtime data (gitignored)
├── export_kb/                  # default export output (optional)
└── tests/
```

### Per-document corpus layout

```text
corpus/<doc_id>/
  meta.json
  source.pdf
  pages/
    0001.png
    0002.png
    …
  blocks.json
  document.md          # current (possibly edited)
  original.md          # first assemble result (for diff)
```

---

## 4. Shared data contracts

### Block

| Field | Type | Meaning |
|-------|------|---------|
| `id` | string | e.g. `1-3` (page-line) |
| `page` | int | 1-based page number |
| `bbox` | `[x0,y0,x1,y1]` | Prefer normalized 0–1 |
| `type` | enum | heading, paragraph, list, table, figure, header, footer, stamp, handwriting |
| `text` | string | Extracted / edited text |
| `conf` | float | 0–1 confidence |
| `engine` | string | `text_layer` or `tesseract` |
| `flags` | string[] | e.g. `low-conf`, `page:scanned` |

### Meta

| Field | Meaning |
|-------|---------|
| `doc_id` | Stable ID (folder name) |
| `agency` | Source agency |
| `status` | `pending` → `reviewed` → `approved` / `rejected` |
| `page_count` | Number of pages |
| `confidence` | Document-level average |
| `sha256` | Hash of original source |
| `url`, `title`, `volatility`, … | Provenance |

### Markdown anchors

Each block is introduced in Markdown as:

```markdown
<!-- b:1-3 -->
Some paragraph text here.
```

The review UI uses these anchors to link the editor to page highlights.

### Status workflow

```text
pending  →  reviewed  →  approved
    ↓           ↓
 rejected   rejected
```

Only **`approved`** documents can be exported to the KB.

---

## 5. Pipeline stages

### 5.1 Normalize

- Input: PDF, images, or Office files (Office needs LibreOffice on PATH).
- Output: `source.pdf` + `pages/0001.png` …
- DPI: view DPI from config (default 150).

### 5.2 Triage

Per page class:

| Class | Meaning |
|-------|---------|
| `clean_text` | Good Unicode text layer |
| `garbled_text` | Broken / legacy encoding |
| `scanned` | Little or no text → need OCR |
| `mixed` | Text + images |

### 5.3 Extract

- Prefer **PDF text layer** when clean.
- Use **OCR (Tesseract)** when scanned/garbled/mixed, or with `--force-ocr`.
- If Tesseract is missing, falls back to text layer and prints a warning.
- Output: `blocks.json`.

### 5.4 Postprocess

- NFC normalization  
- Light Bangla conjunct / spacing repairs  
- Empty block removal  
- Repeated header/footer dropping  

### 5.5 Assemble

- Builds `document.md` with anchors and page markers  
- Saves `original.md` once (for OCR diff)  
- Updates `meta.confidence`  

### 5.6 Review (human)

- Split view: page image | Markdown  
- Edit text, Save, change status  
- Approve only when quality is acceptable  

### 5.7 Export

- Writes `export_kb/<doc_id>.md` (or `MOEDOCS_KB_EXPORT_DIR`)  
- YAML front matter + body Markdown  

---

## 6. CLI reference

All commands (from project root, venv active):

```bat
set PYTHONPATH=src
set MOEDOCS_CORPUS_DIR=corpus
python -m moedocs.cli <command>
```

| Command | Purpose |
|---------|---------|
| `normalize <file>` | PDF/image/Office → corpus pages |
| `extract <doc_id>` | Triage + extract → `blocks.json` |
| `extract <doc_id> --force-ocr` | Always run Tesseract |
| `assemble <doc_id>` | Blocks → `document.md` |
| `pipeline <file>` | normalize + extract + assemble |
| `list` | List corpus documents |
| `show <doc_id>` | Show meta + page list |
| `status <doc_id> <status>` | Set pending/reviewed/approved/rejected |
| `delete <doc_id>` | Remove from corpus |
| `export [doc_id]` | Export one or all approved docs |
| `serve` | Start Review API (port 8000) |
| `info` | Show config paths |

### Examples (Windows CMD)

```bat
python -m moedocs.cli pipeline corpus\DSHE1.pdf --id DSHE1 --agency "DSHE"
python -m moedocs.cli list
python -m moedocs.cli show DSHE1
python -m moedocs.cli status DSHE1 approved
python -m moedocs.cli export DSHE1
python -m moedocs.cli serve
```

---

## 7. Review API

**Base URL (dev):** `http://127.0.0.1:8000`  
Frontend Vite proxies `/api` → that server.

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | Health check |
| GET | `/api/docs` | List documents (`?status=&agency=`) |
| GET | `/api/docs/{id}` | Full doc: meta, markdown, blocks |
| PUT | `/api/docs/{id}/markdown` | Save edited Markdown |
| POST | `/api/docs/{id}/status` | Change status |
| GET | `/api/docs/{id}/diff` | original vs current Markdown |
| GET | `/api/docs/{id}/pages/{n}` | Page meta + blocks |
| GET | `/api/docs/{id}/pages/{n}/image` | Page PNG |
| PATCH | `/api/docs/{id}/blocks/{block_id}` | Edit one block |

Implementation lives under `src/moedocs/review/api/`.

---

## 8. Frontend (Review UI)

**Stack:** React 18, TypeScript, Vite, Zustand, CodeMirror 6, Tailwind  

**Location:** `src/moedocs/review/web/`

### Main UI pieces

| Component | Role |
|-----------|------|
| QueueSidebar | Document list + status badges |
| SourcePane | Page image + prev/next |
| BlockOverlay | Clickable bboxes on the page |
| MarkdownEditor | Editable Markdown with anchors |
| StatusBar | Save / Reviewed / Approve / Reject |
| ConfidenceLegend | Highlight low-confidence blocks |
| DiffToggle | Original OCR vs current text |

### Dev

```bat
cd src\moedocs\review\web
npm install
npm run dev
```

Open **http://localhost:5173** (API must be on port 8000).

---

## 9. Setup (Windows CMD)

### Once

```bat
cd E:\project\moe-docs\moe-docs

python -m venv .venv
.venv\Scripts\activate.bat
pip install -e ".[dev]"

cd src\moedocs\review\web
npm install
cd ..\..\..\..
```

If `python` fails, try `py -m venv .venv`.

### Optional OCR (Tesseract)

1. Install [Tesseract for Windows](https://github.com/UB-Mannheim/tesseract/wiki)  
2. Include **Bengali** language data  
3. In venv:

```bat
pip install pytesseract pillow
```

4. If not on PATH:

```bat
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Default path is also tried automatically in code.

### Optional Office conversion

Install LibreOffice and ensure `libreoffice` is on PATH for `.doc` / `.docx` → PDF.

---

## 10. Runbook — day-to-day

### A. Ingest a document

```bat
cd E:\project\moe-docs\moe-docs
.venv\Scripts\activate.bat
set PYTHONPATH=src
set MOEDOCS_CORPUS_DIR=corpus

python -m moedocs.cli pipeline path\to\file.pdf --id MYDOC --agency "Agency Name"
```

### B. Review UI

**Terminal A — API**

```bat
.venv\Scripts\activate.bat
set PYTHONPATH=src
set MOEDOCS_CORPUS_DIR=corpus
python -m moedocs.cli serve
```

**Terminal B — UI**

```bat
cd src\moedocs\review\web
npm run dev
```

Browser: http://localhost:5173  

Edit → **Save** → **Mark Reviewed** → **Approve**.

### C. Export

```bat
python -m moedocs.cli export MYDOC
REM or all approved:
python -m moedocs.cli export
```

Output default: `export_kb\MYDOC.md`

---

## 11. OCR notes

### Current behaviour

- Digital PDFs with a text layer: no Tesseract required.  
- Scans / garbled / `--force-ocr`: Tesseract `ben+eng`.  
- Quality on complex Bangla forms can be poor until engines/layout improve.

### Known issues

- Text layer may use broken encodings → garbage in Markdown while the **image** looks correct.  
- Line-level blocks (not merged paragraphs) → many small blocks.  
- Tables are not structure-aware yet (stub only).

### Benchmark (Milestone 2)

Place gold pairs in `bench/gold/`:

```text
page001.png
page001.txt   ← human-corrected UTF-8
```

Run:

```bat
set PYTHONPATH=src
python bench\run_bench.py
```

Metrics: **CER**, **WER**, **conjunct error rate**.

### Later improvements (Milestone 9)

- Second engine (Surya / Paddle)  
- Line → paragraph merging  
- Table recognition  
- Better Bangla postprocess  

---

## 12. Export to chatbot KB

### Output format

```markdown
---
doc_id: DSHE1
title: DSHE1
agency: DSHE
status: approved
confidence: 0.950
page_count: 2
source: DSHE1.pdf
url: 
sha256: ...
exported_at: 2026-10-08T...
---

# DSHE1

<!-- page:1 -->
<!-- b:1-1 -->
...
```

### Config

In `.env`:

```env
MOEDOCS_KB_EXPORT_DIR=E:\project\moe-bot\data\kb
```

Or omit to use `./export_kb`.

The chatbot’s ingest script should load these Markdown files (front matter + body).

---

## 13. Milestones status

| # | Milestone | Status |
|---|-----------|--------|
| 1 | Foundations: schema, store, normalize, CLI, API skeleton | Done |
| 2 | OCR benchmark (CER/WER/conjunct) | Done |
| 3 | Extraction MVP (triage → extract → postprocess → assemble) | Done |
| 4 | Review UI read-only + Windows runbook | Done |
| 5 | Editing + status workflow (Save / Approve) | Done |
| 6 | Diff polish / UX extras | Partial (diff toggle exists) |
| 7 | Export approved → KB Markdown | Done |
| 8 | Acquire / crawler + change detection | Not started |
| 9 | Second OCR engine, tables, SFT builder, PII | Not started |

---

## 14. Configuration

Environment variables (prefix `MOEDOCS_`), see `.env.example`:

| Variable | Default | Meaning |
|----------|---------|---------|
| `MOEDOCS_CORPUS_DIR` | `./corpus` | Document storage |
| `MOEDOCS_SOURCES_FILE` | `./sources.yml` | Crawl config |
| `MOEDOCS_KB_EXPORT_DIR` | (none) | Export folder |
| `MOEDOCS_OCR_ENGINE` | `tesseract` | Default engine name |
| `MOEDOCS_TESSERACT_LANG` | `ben+eng` | Tesseract languages |
| `MOEDOCS_VIEW_DPI` | `150` | Page image DPI for UI |
| `MOEDOCS_OCR_DPI` | `300` | OCR render DPI (future use) |
| `MOEDOCS_API_HOST` | `0.0.0.0` | API bind host |
| `MOEDOCS_API_PORT` | `8000` | API port |
| `TESSERACT_CMD` | (auto) | Full path to `tesseract.exe` on Windows |

Copy `.env.example` → `.env` and edit. **Do not commit `.env`.**

---

## 15. Git

```bat
git status
git add <files>
git commit -m "Describe change"
```

### What is ignored

- `.venv/`, `__pycache__/`, `*.egg-info/`  
- `.env` (secrets)  
- `corpus/` (runtime data)  
- `node_modules/`, `dist/`  
- IDE / OS junk  

`.env.example` **is** tracked.

---

## 16. Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: moedocs` | `set PYTHONPATH=src` in that CMD window |
| `python` not found | Use `py` instead |
| Queue empty in UI | Run `pipeline`; confirm `corpus\<id>\meta.json` exists |
| Page images 404 | Check `corpus\<id>\pages\0001.png` |
| Frontend cannot reach API | API on port 8000; restart `serve` |
| `pytesseract` / Tesseract errors | Install Tesseract + `pip install pytesseract`; set `TESSERACT_CMD` |
| OCR text is garbage | Common on hard layouts; use text layer when good, or improve later with better engines |
| Cannot export | Document must be **approved** first |
| Office file fails normalize | Install LibreOffice headless |
| Port 8000 in use | `python -m moedocs.cli serve --port 8001` (update Vite proxy if needed) |

---

## Quick reference card (Windows)

```bat
cd E:\project\moe-docs\moe-docs
.venv\Scripts\activate.bat
set PYTHONPATH=src
set MOEDOCS_CORPUS_DIR=corpus

python -m moedocs.cli pipeline myfile.pdf --id MYDOC --agency "Agency"
python -m moedocs.cli serve

REM other terminal:
cd src\moedocs\review\web
npm run dev

REM after Approve in UI:
python -m moedocs.cli export MYDOC
```

---

*End of documentation. For short daily steps see `docs/runbook.md`.*
