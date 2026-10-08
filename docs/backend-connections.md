# Backend ↔ Frontend Connection Map

This document explains **exactly** which backend endpoints the frontend calls, what data shapes are expected, and how the pieces fit together.

---

## 1. High-level connection diagram

```
┌─────────────────────────────────────┐
│          React Review UI            │
│  (Vite :5173)                       │
│                                     │
│  api/client.ts  ────────────────────┼──►  /api/*  (proxied)
└─────────────────────────────────────┘         │
                                                ▼
┌─────────────────────────────────────┐
│          FastAPI Review API         │
│  (uvicorn :8000)                    │
│                                     │
│  review/api/                        │
│    main.py                          │
│    routes_docs.py                   │
│    routes_pages.py                  │
│    routes_edit.py                   │
│                                     │
│  reads/writes via store.py ─────────┼──►  corpus/<doc_id>/
│                                     │       source.pdf
│                                     │       pages/*.png
│                                     │       blocks.json
│                                     │       document.md
│                                     │       meta.json
└─────────────────────────────────────┘
```

The frontend **never** touches the filesystem. All persistence goes through the FastAPI layer → `store.py`.

---

## 2. API Contract (what the frontend expects)

All responses are JSON unless noted. Types are defined in both:

- Frontend: `src/types/index.ts`
- Backend:  `src/moedocs/schema.py` (Pydantic)

### 2.1 List documents

```
GET /api/docs?status=pending&agency=...
```

**Response** `DocumentSummary[]`:

```json
[
  {
    "doc_id": "moe-2024-circular-12",
    "agency": "Ministry of Education",
    "status": "pending",
    "page_count": 4,
    "confidence": 0.87,
    "title": "Circular regarding ...",
    "retrieved_at": "2026-03-15T10:22:00Z"
  }
]
```

Used by: `QueueSidebar` via `store.loadDocuments()`.

---

### 2.2 Get full document

```
GET /api/docs/{doc_id}
```

**Response** `DocumentDetail`:

```json
{
  "meta": { ...Meta },
  "markdown": "# Title\n\n<!-- b:1 -->\nParagraph text...",
  "blocks": [ ...Block ],
  "page_count": 4,
  "confidence": 0.87,
  "original_markdown": "..."   // optional, for diff view
}
```

Used by: `store.selectDocument()`.

---

### 2.3 Get page info + image

```
GET /api/docs/{doc_id}/pages/{page}
```

**Response** `PageInfo`:

```json
{
  "page": 1,
  "image_url": "/api/docs/moe-2024.../pages/1/image",
  "width": 1654,
  "height": 2339,
  "blocks": [ ... only blocks for this page ]
}
```

```
GET /api/docs/{doc_id}/pages/{page}/image
```

Returns the raw PNG (or JPEG) of the page.  
Used by: `<img src={pageImageUrl(...)} />` inside `SourcePane`.

---

### 2.4 Edit a single block

```
PATCH /api/docs/{doc_id}/blocks/{block_id}
Content-Type: application/json

{ "text": "new text", "type": "heading", "flags": ["low-conf"] }
```

**Response** the updated `Block`.

Used by: future inline block editing; currently the main path is full-markdown save.

---

### 2.5 Save whole Markdown

```
PUT /api/docs/{doc_id}/markdown
Content-Type: application/json

{ "markdown": "full document markdown with anchors" }
```

Backend should:
1. Parse the new anchors / text
2. Optionally re-align blocks
3. Write `document.md`
4. Update `blocks.json` if necessary

Used by: `StatusBar` → `store.saveMarkdown()`.

---

### 2.6 Change status

```
POST /api/docs/{doc_id}/status
Content-Type: application/json

{ "status": "approved" }
```

Valid transitions (enforced by backend):

```
pending  → reviewed | rejected
reviewed → approved | rejected
approved → (terminal, or allow re-open later)
rejected → pending (optional)
```

When status becomes `approved`, the backend may automatically call the export module.

Used by: `StatusBar` buttons.

---

### 2.7 Diff (optional)

```
GET /api/docs/{doc_id}/diff
```

**Response**:

```json
{
  "original": "raw OCR markdown",
  "current": "edited markdown"
}
```

Used when the user toggles “Show OCR Diff”.

---

## 3. How the backend modules feed the Review API

| Backend module   | What it produces                     | How Review API uses it                          |
|------------------|--------------------------------------|-------------------------------------------------|
| `normalize`      | `source.pdf` + `pages/*.png`         | Page images served by `/pages/{n}/image`        |
| `triage`         | page class (clean/scan/mixed)        | Stored in meta or blocks for diagnostics        |
| `extract`        | raw `blocks.json`                    | Base data for the document                      |
| `postprocess`    | cleaned blocks                       | Final text that goes into Markdown              |
| `assemble`       | `document.md` + confidence scores    | Served as `markdown` + `confidence`             |
| `store`          | filesystem abstraction               | All read/write of corpus/ goes through here     |
| `export`         | KB Markdown + SFT                    | Triggered after status → `approved`             |

The Review API is intentionally **thin**. It mostly:
1. Reads from `store`
2. Applies small mutations (text, status)
3. Writes back via `store`
4. Optionally triggers `export` on approve

---

## 4. Shared types (must stay in sync)

| Field / Model | Frontend (`types/index.ts`) | Backend (`schema.py`) |
|---------------|-----------------------------|-----------------------|
| `Block`       | interface                   | Pydantic model        |
| `Meta`        | interface                   | Pydantic model        |
| `DocStatus`   | union type                  | Literal / Enum        |
| `bbox`        | `[number, number, number, number]` | `tuple[float, float, float, float]` |

**Convention for `bbox`**:
- Prefer normalized coordinates `0.0 – 1.0` (page-relative).
- Frontend scales them to pixel coordinates using the actual image size.
- Absolute pixel coordinates are also accepted (detected by `x1 > 1.01`).

**Markdown anchors**:
```
<!-- b:12 -->
```
The number (or string id) must match `Block.id`.  
This is the only link between the text editor and the visual overlay.

---

## 5. Recommended backend route files

```
src/moedocs/review/api/
├── main.py              # FastAPI app, CORS, mount
├── routes_docs.py       # list + get document, status, markdown
├── routes_pages.py      # page info + image serving
└── routes_edit.py       # block PATCH, future batch edits
```

Example skeleton for `main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes_docs import router as docs_router
from .routes_pages import router as pages_router
from .routes_edit import router as edit_router

app = FastAPI(title="moe-docs Review API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(docs_router, prefix="/api")
app.include_router(pages_router, prefix="/api")
app.include_router(edit_router, prefix="/api")
```

---

## 6. Development workflow

1. Start backend:
   ```bash
   uvicorn moedocs.review.api.main:app --reload --port 8000
   ```

2. Start frontend:
   ```bash
   cd src/moedocs/review/web
   npm run dev
   ```

3. Open http://localhost:5173  
   All `/api/*` calls are proxied automatically by Vite.

---

## 7. What is intentionally **not** in the frontend

- No OCR, no layout analysis, no Bangla post-processing
- No direct filesystem access
- No knowledge of `sources.yml` or the acquire pipeline
- No export logic (that stays in the backend `export/` module)

The frontend is a pure review & editing surface.
