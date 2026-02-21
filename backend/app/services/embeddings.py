"""Semantic search via Voyage AI embeddings + pgvector.

Voyage AI is Anthropic's embedding model provider.
The ANTHROPIC_API_KEY is also valid for Voyage AI.
Voyage-3 produces 1024-dimensional vectors.
"""
import os
import httpx
from typing import List

EMBEDDING_DIM = 1024  # voyage-3 default dimension
VOYAGE_API_URL = "https://api.voyageai.com/v1/embeddings"
VOYAGE_MODEL = "voyage-3"


def generate_embedding(text: str) -> List[float]:
    """Generate 1024-dim embedding via Voyage AI (voyage-3 model).

    Uses ANTHROPIC_API_KEY which is valid for Voyage AI as well.
    Returns zero vector on failure (semantic search gracefully disabled).
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return [0.0] * EMBEDDING_DIM

    text = (text or "").strip()
    if not text:
        return [0.0] * EMBEDDING_DIM

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                VOYAGE_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": VOYAGE_MODEL,
                    "input": [text[:8000]],
                    "input_type": "document",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            embedding = data["data"][0]["embedding"]
            if len(embedding) != EMBEDDING_DIM:
                print(f"[embeddings] Unexpected dim: {len(embedding)}, expected {EMBEDDING_DIM}")
                # Resize if needed
                if len(embedding) > EMBEDDING_DIM:
                    embedding = embedding[:EMBEDDING_DIM]
                else:
                    embedding += [0.0] * (EMBEDDING_DIM - len(embedding))
            return embedding
    except Exception as e:
        print(f"[embeddings] Failed to generate embedding: {e}")
        return [0.0] * EMBEDDING_DIM


def generate_query_embedding(query: str) -> List[float]:
    """Generate embedding for search queries (input_type=query)."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return [0.0] * EMBEDDING_DIM

    query = (query or "").strip()
    if not query:
        return [0.0] * EMBEDDING_DIM

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                VOYAGE_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": VOYAGE_MODEL,
                    "input": [query[:2000]],
                    "input_type": "query",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            embedding = data["data"][0]["embedding"]
            if len(embedding) > EMBEDDING_DIM:
                embedding = embedding[:EMBEDDING_DIM]
            elif len(embedding) < EMBEDDING_DIM:
                embedding += [0.0] * (EMBEDDING_DIM - len(embedding))
            return embedding
    except Exception as e:
        print(f"[embeddings] Query embedding failed: {e}")
        return [0.0] * EMBEDDING_DIM


def is_zero_vector(embedding: List[float]) -> bool:
    """Check if embedding is the fallback zero vector."""
    return all(v == 0.0 for v in embedding)


def cosine_similarity_search(
    query_embedding: List[float],
    db,
    tenant_id: str = "default",
    limit: int = 10,
    min_similarity: float = 0.5,
) -> list:
    """Search papers by cosine similarity using pgvector operator <=>."""
    from sqlalchemy import text

    embedding_str = f"[{','.join(map(str, query_embedding))}]"

    result = db.execute(
        text("""
            SELECT
                id, name, paper_type, date, reference,
                1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
            FROM papers
            WHERE
                embedding IS NOT NULL
                AND tenant_id = :tenant_id
                AND deleted = false
            ORDER BY embedding <=> CAST(:embedding AS vector)
            LIMIT :limit
        """),
        {
            "embedding": embedding_str,
            "tenant_id": tenant_id,
            "limit": limit,
        },
    )

    rows = result.fetchall()
    return [r for r in rows if r.similarity >= min_similarity]
