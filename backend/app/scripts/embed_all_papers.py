"""
embed_all_papers.py - Batch-Embedding fuer bestehende Drucksachen.

Aufruf: python -m app.scripts.embed_all_papers
        oder: python /app/app/scripts/embed_all_papers.py

Generiert Voyage AI Embeddings (voyage-3, 1024 dim) fuer alle Papers
ohne existierendes Embedding und speichert sie in der DB.
"""
import sys
import os
import time

# Add /app to path when running standalone
if "/app" not in sys.path:
    sys.path.insert(0, "/app")

from sqlalchemy import text
from app.database import SessionLocal
from app.models.oparl import Paper
from app.services.embeddings import generate_embedding, is_zero_vector, EMBEDDING_DIM


def embed_all_papers(batch_size: int = 50, delay_ms: int = 100):
    """Generate and store embeddings for all papers without one.

    Args:
        batch_size: How many papers to embed per run (to avoid timeouts)
        delay_ms: Delay between API calls in milliseconds (rate limiting)
    """
    db = SessionLocal()
    try:
        # Count total needing embedding
        total_pending = db.execute(
            text("SELECT COUNT(*) FROM papers WHERE deleted = false AND embedding IS NULL")
        ).scalar() or 0

        if total_pending == 0:
            print("[embed_all] Alle Papers bereits eingebettet.")
            return

        print(f"[embed_all] {total_pending} Papers ohne Embedding gefunden.")
        print(f"[embed_all] Verarbeite {min(batch_size, total_pending)} in diesem Lauf...")

        # Fetch batch
        papers = (
            db.query(Paper)
            .filter(Paper.deleted == False, Paper.embedding == None)
            .limit(batch_size)
            .all()
        )

        success_count = 0
        skip_count = 0

        for i, paper in enumerate(papers):
            # Build rich text for embedding
            text_parts = []
            if paper.name:
                text_parts.append(paper.name)
            if hasattr(paper, "description") and paper.description:
                text_parts.append(paper.description)
            if paper.paper_type:
                text_parts.append(f"Typ: {paper.paper_type}")
            if paper.keyword:
                text_parts.append(f"Stichwoerter: {', '.join(paper.keyword)}")
            if paper.reference:
                text_parts.append(f"Drucksache: {paper.reference}")

            text_content = " ".join(text_parts)[:8000]

            if not text_content.strip():
                skip_count += 1
                continue

            embedding = generate_embedding(text_content)

            if is_zero_vector(embedding):
                print(f"[embed_all] Embedding-Service nicht verfuegbar. Abbruch.")
                break

            embedding_str = f"[{','.join(map(str, embedding))}]"
            db.execute(
                text("UPDATE papers SET embedding = CAST(:emb AS vector) WHERE id = :id"),
                {"emb": embedding_str, "id": paper.id},
            )

            success_count += 1

            # Commit every 10 papers
            if success_count % 10 == 0:
                db.commit()
                print(f"  [{i+1}/{len(papers)}] {success_count} eingebettet...")

            # Rate limiting
            if delay_ms > 0:
                time.sleep(delay_ms / 1000)

        db.commit()
        print(f"\n[embed_all] Fertig!")
        print(f"  Eingebettet: {success_count}")
        print(f"  Uebersprungen (kein Text): {skip_count}")
        print(f"  Noch ausstehend: {total_pending - success_count}")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch-Embedding fuer Drucksachen")
    parser.add_argument("--batch-size", type=int, default=50, help="Papers pro Lauf")
    parser.add_argument("--delay-ms", type=int, default=100, help="Verzoegerung zwischen API-Calls (ms)")
    args = parser.parse_args()

    embed_all_papers(batch_size=args.batch_size, delay_ms=args.delay_ms)
