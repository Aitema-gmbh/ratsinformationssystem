"""
aitema|RIS - Semantic Search Router

FastAPI Router fuer semantische Suche via pgvector + Voyage AI Embeddings:
- POST /api/v1/search/semantic              - Semantische Volltextsuche
- POST /api/v1/search/semantic/embed/{id}  - Einzelnes Paper einbetten
- GET  /api/v1/search/semantic/status      - Status der Embedding-Abdeckung
"""
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.models.oparl import Paper
from app.services.embeddings import (
    generate_embedding,
    generate_query_embedding,
    cosine_similarity_search,
    is_zero_vector,
    EMBEDDING_DIM,
)

router = APIRouter(prefix="/api/v1/search", tags=["Semantische Suche"])


# ============================================================
# Pydantic Schemas
# ============================================================

class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 10
    min_similarity: float = 0.5
    tenant_id: str = "default"


class SemanticResult(BaseModel):
    id: str
    name: Optional[str] = None
    paper_type: Optional[str] = None
    date: Optional[str] = None
    reference: Optional[str] = None
    similarity_score: float


class SemanticSearchResponse(BaseModel):
    results: list[SemanticResult]
    mode: str
    query: str
    total: int
    message: Optional[str] = None


class EmbedResponse(BaseModel):
    status: str
    paper_id: str
    message: Optional[str] = None


class EmbeddingStatusResponse(BaseModel):
    total_papers: int
    embedded_papers: int
    coverage_percent: float
    semantic_search_enabled: bool


# ============================================================
# POST /api/v1/search/semantic
# ============================================================

@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    db: Session = Depends(get_db),
):
    """Semantische Suche ueber alle Drucksachen via Cosine-Similarity.

    Nutzt Voyage AI (voyage-3, 1024 Dimensionen) fuer Embeddings.
    Erfordert ANTHROPIC_API_KEY als Umgebungsvariable.
    """
    query = (request.query or "").strip()
    if len(query) < 2:
        return SemanticSearchResponse(
            results=[],
            mode="semantic",
            query=query,
            total=0,
            message="Suchbegriff zu kurz (min. 2 Zeichen)",
        )

    # Generate query embedding
    query_embedding = generate_query_embedding(query)

    if is_zero_vector(query_embedding):
        return SemanticSearchResponse(
            results=[],
            mode="semantic_disabled",
            query=query,
            total=0,
            message=(
                "Semantische Suche nicht verfuegbar. "
                "ANTHROPIC_API_KEY fehlt oder Embedding-Service nicht erreichbar."
            ),
        )

    # Search via pgvector
    rows = cosine_similarity_search(
        query_embedding=query_embedding,
        db=db,
        tenant_id=request.tenant_id,
        limit=request.limit,
        min_similarity=request.min_similarity,
    )

    results = [
        SemanticResult(
            id=str(row.id),
            name=row.name,
            paper_type=row.paper_type,
            date=str(row.date) if row.date else None,
            reference=row.reference,
            similarity_score=round(float(row.similarity) * 100, 1),
        )
        for row in rows
    ]

    return SemanticSearchResponse(
        results=results,
        mode="semantic",
        query=query,
        total=len(results),
    )


# ============================================================
# POST /api/v1/search/semantic/embed/{paper_id}
# ============================================================

@router.post("/semantic/embed/{paper_id}", response_model=EmbedResponse)
async def embed_paper(
    paper_id: str,
    db: Session = Depends(get_db),
):
    """Embedding fuer ein einzelnes Paper generieren und speichern."""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} nicht gefunden")

    # Combine text fields for rich embedding
    text_content = " ".join(filter(None, [
        paper.name or "",
        getattr(paper, "description", "") or "",
        " ".join(paper.keyword or []) if paper.keyword else "",
        paper.paper_type or "",
    ]))[:8000]

    embedding = generate_embedding(text_content)

    if is_zero_vector(embedding):
        return EmbedResponse(
            status="skipped",
            paper_id=paper_id,
            message="Embedding-Service nicht verfuegbar (ANTHROPIC_API_KEY fehlt)",
        )

    embedding_str = f"[{','.join(map(str, embedding))}]"
    db.execute(
        text("UPDATE papers SET embedding = CAST(:emb AS vector) WHERE id = :id"),
        {"emb": embedding_str, "id": paper_id},
    )
    db.commit()

    return EmbedResponse(
        status="embedded",
        paper_id=paper_id,
        message=f"Embedding ({EMBEDDING_DIM} Dimensionen) gespeichert",
    )


# ============================================================
# GET /api/v1/search/semantic/status
# ============================================================

@router.get("/semantic/status", response_model=EmbeddingStatusResponse)
async def embedding_status(db: Session = Depends(get_db)):
    """Status der Embedding-Abdeckung aller Drucksachen."""
    total = db.execute(
        text("SELECT COUNT(*) FROM papers WHERE deleted = false")
    ).scalar() or 0

    embedded = db.execute(
        text("SELECT COUNT(*) FROM papers WHERE deleted = false AND embedding IS NOT NULL")
    ).scalar() or 0

    import os
    has_key = bool(os.getenv("ANTHROPIC_API_KEY"))

    coverage = round((embedded / total * 100), 1) if total > 0 else 0.0

    return EmbeddingStatusResponse(
        total_papers=total,
        embedded_papers=embedded,
        coverage_percent=coverage,
        semantic_search_enabled=has_key,
    )
