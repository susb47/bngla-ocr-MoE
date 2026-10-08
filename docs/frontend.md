# Frontend Architecture – moe-docs Review UI

## Overview

The review UI is a React + TypeScript single-page application that lets a human:
- Browse the document queue (pending / reviewed / approved / rejected)
- View the original page image side-by-side with the extracted Markdown
- Click a block on the page → jump to the corresponding `<!-- b:N -->` anchor in the editor
- Edit the Markdown, change block types/flags, and change document status
- Toggle confidence highlighting and OCR-diff mode
- Save changes and Approve / Reject

It talks **only** to the FastAPI backend under `/api/*`.

---

## Tech Stack

| Piece              | Choice                          | Why                                      |
|--------------------|---------------------------------|------------------------------------------|
| Build              | Vite 6                          | Fast HMR, simple proxy                   |
| UI library         | React 18 + TypeScript           | Industry standard                        |
| State              | Zustand                         | Tiny, no boilerplate                     |
| Editor             | CodeMirror 6 (`@uiw/react-codemirror`) | Excellent Markdown support, extensible |
| Preview            | markdown-it                     | Lightweight, no React overhead           |
| Page rendering     | Backend-rendered PNG + overlay  | Simple; can later swap for pdf.js        |
| Styling            | Tailwind CSS                    | Utility-first, rapid UI                  |
| Routing            | None (single view)              | Queue + split pane is enough for v1      |

---

## File Tree (Frontend only)

```
src/moedocs/review/web/
├── package.json
├── vite.config.ts          # proxy /api → :8000
├── tsconfig.json
├── tsconfig.node.json
├── index.html
├── postcss.config.js
├── tailwind.config.js
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    ├── vite-env.d.ts
    ├── api/
    │   └── client.ts       # all HTTP calls to FastAPI
    ├── types/
    │   └── index.ts        # mirrors backend schema.py
    ├── state/
    │   ├── store.ts        # Zustand store (source of truth)
    │   └── sync.ts         # anchor ↔ block helpers
    └── components/
        ├── QueueSidebar.tsx
        ├── SplitLayout.tsx
        ├── SourcePane.tsx
        ├── BlockOverlay.tsx
        ├── MarkdownEditor.tsx
        ├── MarkdownPreview.tsx
        ├── ConfidenceLegend.tsx
        ├── DiffToggle.tsx
        └── StatusBar.tsx
```

---

## Component Responsibilities

| Component          | Responsibility |
|--------------------|----------------|
| `App`              | Shell, header, error banner, loads initial queue |
| `QueueSidebar`     | Document list + status badges + confidence summary |
| `SplitLayout`      | 50/50 split; switches to diff mode when toggled |
| `SourcePane`       | Page navigator + page image + BlockOverlay |
| `BlockOverlay`     | Absolute-positioned clickable rectangles over the image |
| `MarkdownEditor`   | CodeMirror instance; scrolls to anchor on block select |
| `MarkdownPreview`  | Read-only rendered Markdown (used in diff mode) |
| `ConfidenceLegend` | Toggle + threshold slider for low-confidence highlighting |
| `DiffToggle`       | Show/hide original OCR vs current text |
| `StatusBar`        | Save, Mark Reviewed, Approve, Reject buttons + stats |

---

## Data Flow (Frontend)

```
User action
    │
    ▼
Zustand store (store.ts)
    │
    ├── loadDocuments() ──────────────► GET  /api/docs
    ├── selectDocument(id) ───────────► GET  /api/docs/{id}
    ├── updateEditBuffer(md)          (local only)
    ├── saveMarkdown() ───────────────► PUT  /api/docs/{id}/markdown
    ├── updateBlockText(id, text) ────► PATCH /api/docs/{id}/blocks/{id}
    └── setStatus(status) ────────────► POST /api/docs/{id}/status
```

All API calls live in `api/client.ts`. The Vite dev server proxies `/api` to `http://localhost:8000`.

---

## Key UX Behaviours

1. **Linked selection**  
   Click a bbox on the page → `selectedBlockId` is set → editor scrolls to `<!-- b:XX -->`.

2. **Confidence overlay**  
   Blocks with `conf < threshold` get a red tint. Threshold is adjustable.

3. **Dirty state**  
   Any change to the Markdown marks the document dirty; “Save” becomes active.

4. **Status workflow**  
   `pending → reviewed → approved` (or `rejected` at any time).  
   Only `approved` documents are exported by the backend.

5. **Diff mode**  
   When `original_markdown` is present, the right pane splits into Original OCR | Current.

---

## How to run (dev)

```bash
cd src/moedocs/review/web
npm install
npm run dev          # http://localhost:5173
```

The FastAPI backend must be running on port 8000 (or change the proxy target in `vite.config.ts`).
