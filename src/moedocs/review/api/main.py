"""FastAPI application for the review UI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes_docs import router as docs_router
from .routes_pages import router as pages_router
from .routes_edit import router as edit_router

app = FastAPI(
    title="moe-docs Review API",
    version="0.1.0",
    description="Human review gate for the Bangla Document Pipeline",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(docs_router, prefix="/api")
app.include_router(pages_router, prefix="/api")
app.include_router(edit_router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
