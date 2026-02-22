"""
aitema|RIS - RAG Chat Router (E1)

Endpoint: POST /api/rag/chat
Retrieval-Augmented Generation ueber Ratsbeschluesse mit Claude Haiku + Streaming.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import anthropic
import json
import os

from app.database import get_db
from app.services.embeddings import generate_query_embedding, is_zero_vector
from sqlalchemy import text

router = APIRouter(prefix="/api/rag", tags=["rag"])


class RAGQuery(BaseModel):
    query: str
    tenant_id: str = "default"
    limit: int = 8


@router.post("/chat")
async def rag_chat(body: RAGQuery, db: Session = Depends(get_db)):
    """RAG-Chat ueber Ratsbeschluesse: Vektor-Suche + Claude Haiku Streaming."""

    # 1. Query-Embedding generieren (Voyage AI via ANTHROPIC_API_KEY)
    query_embedding = generate_query_embedding(body.query)

    if is_zero_vector(query_embedding):
        async def no_key():
            yield "data: " + json.dumps({"text": "Semantische Suche nicht verfuegbar (API-Key fehlt)."}) + "\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(no_key(), media_type="text/event-stream")

    embedding_str = f"[{','.join(map(str, query_embedding))}]"

    # 2. pgvector Suche direkt auf papers-Tabelle (embedding-Spalte)
    rows = db.execute(text("""
        SELECT
            id,
            name,
            paper_type,
            date,
            reference,
            COALESCE(ai_summary, '') AS content,
            1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
        FROM papers
        WHERE
            embedding IS NOT NULL
            AND tenant_id = :tenant_id
            AND deleted = false
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :limit
    """), {
        "embedding": embedding_str,
        "tenant_id": body.tenant_id,
        "limit": body.limit,
    }).fetchall()

    if not rows:
        async def no_results():
            yield "data: " + json.dumps({"text": "Keine relevanten Beschluesse gefunden. Bitte pruefen Sie, ob Embeddings fuer die Drucksachen generiert wurden."}) + "\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(no_results(), media_type="text/event-stream")

    # 3. Kontext aufbauen (nur Treffer mit >= 30% Aehnlichkeit)
    context_parts = []
    sources = []
    for r in rows:
        if r.similarity < 0.3:
            continue
        # Bevorzuge KI-Zusammenfassung, sonst Drucksachentyp als Fallback
        text_snippet = r.content.strip() if r.content.strip() else (r.paper_type or "")
        context_parts.append(
            f"**{r.name or 'Ohne Titel'}** (Drucksache {r.reference or '?'}, {r.date})\n{text_snippet[:600]}"
        )
        sources.append({
            "id": r.id,
            "title": r.name or "Ohne Titel",
            "reference": r.reference or "",
            "date": str(r.date) if r.date else "",
            "similarity": round(float(r.similarity) * 100, 1),
        })

    if not context_parts:
        # Treffer vorhanden, aber alle unter Schwellwert – trotzdem die besten 3 nehmen
        for r in rows[:3]:
            text_snippet = r.content.strip() if r.content.strip() else (r.paper_type or "")
            context_parts.append(
                f"**{r.name or 'Ohne Titel'}** (Drucksache {r.reference or '?'}, {r.date})\n{text_snippet[:600]}"
            )
            sources.append({
                "id": r.id,
                "title": r.name or "Ohne Titel",
                "reference": r.reference or "",
                "date": str(r.date) if r.date else "",
                "similarity": round(float(r.similarity) * 100, 1),
            })

    context = "\n\n---\n\n".join(context_parts)

    system_prompt = (
        "Du bist ein Assistent fuer das Ratsinformationssystem einer deutschen Kommune. "
        "Beantworte die Frage des Buergers ausschliesslich auf Basis der bereitgestellten "
        "Beschluesse und Vorlagen. Wenn die Information nicht in den Quellen enthalten ist, "
        "sage das klar. Antworte auf Deutsch, sachlich und neutral. "
        "Zitiere konkrete Drucksachen-Nummern oder Beschluesse wenn moeglich."
    )

    user_message = f"Kontext aus dem Ratsinformationssystem:\n\n{context}\n\nFrage: {body.query}"

    # 4. Anthropic Client + Streaming
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        async def no_anthropic_key():
            yield "data: " + json.dumps({"text": "ANTHROPIC_API_KEY nicht gesetzt."}) + "\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(no_anthropic_key(), media_type="text/event-stream")

    client = anthropic.Anthropic(api_key=api_key)

    async def stream_response():
        # Zuerst Quellen senden
        yield "data: " + json.dumps({"sources": sources}) + "\n\n"

        try:
            with client.messages.stream(
                model="claude-haiku-4-5",
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            ) as stream:
                for chunk in stream.text_stream:
                    yield "data: " + json.dumps({"text": chunk}) + "\n\n"
        except Exception as e:
            yield "data: " + json.dumps({"text": f"\n\n[Fehler: {str(e)}]"}) + "\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
