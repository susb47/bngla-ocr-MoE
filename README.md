# moe-docs

**Bangla Document Pipeline** — turn official Bangla documents (digital + scanned) into reviewed, traceable Markdown for a chatbot knowledge base and training set.

This is a **standalone project**. It exports into the chatbot’s `data/kb/` folder; it does not live inside the chatbot repo.

## Principles

1. **Traceability** — every Markdown block points back to a page + bounding box
2. **Page-level decisions** — mixed PDFs are handled page by page
3. **Human gate** — only reviewed/approved documents are exported
4. **Pluggable OCR engines** — one interface, benchmark picks the winner
5. **Separate repo** — this project owns the pipeline; the chatbot only consumes the output

## Quick start

```bash
# 1. Clone / enter the project
cd moe-docs

# 2. Python backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 3. Frontend (review UI)
cd src/moedocs/review/web
npm install
cd ../../../../

# 4. Copy env
cp .env.example .env
```

### Run the review UI (dev)

```bash
# Terminal 1 – FastAPI backend (once Milestone 1+ is implemented)
uvicorn moedocs.review.api.main:app --reload --port 8000

# Terminal 2 – React frontend
cd src/moedocs/review/web
npm run dev
# → http://localhost:5173
```

## Project layout

```
moe-docs/
├── README.md
├── pyproject.toml
├── .env.example
├── sources.yml
├── docs/                     # architecture, frontend, backend connections
├── src/moedocs/              # Python package
│   ├── acquire/ normalize/ triage/ extract/ postprocess/
│   ├── assemble/ export/
│   └── review/
│       ├── api/              # FastAPI
│       └── web/              # React + Vite frontend (fully scaffolded)
├── bench/                    # OCR quality evaluation
├── corpus/                   # runtime data (gitignored)
└── tests/
```

See `docs/file-tree.md` for the complete tree.

## Documentation

| Doc | Description |
|-----|-------------|
| `docs/frontend.md` | React UI architecture & components |
| `docs/backend-connections.md` | API contract, how FE ↔ BE talk |
| `docs/file-tree.md` | Full file tree |
| `docs/architecture.md` | System design (to be expanded) |


### Full pipeline (normalize → extract → assemble)

```bash
PYTHONPATH=src MOEDOCS_CORPUS_DIR=./corpus \
  python -m moedocs.cli pipeline path/to/file.pdf --agency "MoE"

# Or step by step:
python -m moedocs.cli normalize file.pdf --id my-doc
python -m moedocs.cli extract my-doc
python -m moedocs.cli assemble my-doc
python -m moedocs.cli show my-doc
```

### OCR benchmark

```bash
# Add gold pairs under bench/gold/ (page.png + page.txt)
PYTHONPATH=src python bench/run_bench.py
```

## Status

- [x] Frontend review UI (complete scaffold)
- [x] Project structure + docs
- [x] Milestone 1 – schema, store, config, normalize, CLI, Review API skeleton
- [x] Milestone 2 – OCR benchmark (CER/WER/conjunct ER + gold layout)
- [x] Milestone 3 – Extraction MVP (triage → extract → postprocess → assemble)
- [ ] Milestone 4–6 – Full review editing workflow
- [ ] Milestone 7 – Export to KB
- [ ] Milestone 8 – Acquire / crawler
- [ ] Milestone 9 – Second engine, tables, SFT builder

## License

Internal / private – adjust as needed.
