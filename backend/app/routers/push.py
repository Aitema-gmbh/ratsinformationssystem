"""
aitema|RIS - Web Push Notifications Router (E3)

Endpunkte:
  GET    /api/push/vapid-public-key  - VAPID Public Key fuer Frontend
  POST   /api/push/subscribe         - Push-Abonnement speichern
  DELETE /api/push/unsubscribe       - Push-Abonnement loeschen
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
import json
import os

from app.database import get_db

router = APIRouter(prefix="/api/push", tags=["push"])


class PushSubscription(BaseModel):
    endpoint: str
    keys: dict
    topic: Optional[str] = None


def ensure_table(db: Session):
    """Create push_subscriptions table if it does not exist."""
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id SERIAL PRIMARY KEY,
            endpoint TEXT UNIQUE NOT NULL,
            p256dh TEXT NOT NULL,
            auth TEXT NOT NULL,
            topic TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """))
    db.commit()


@router.get("/vapid-public-key")
def get_vapid_key():
    """Return the VAPID public key for client-side subscription setup."""
    key = os.environ.get("VAPID_PUBLIC_KEY", "")
    if not key:
        raise HTTPException(status_code=500, detail="VAPID_PUBLIC_KEY not configured")
    return {"key": key}


@router.post("/subscribe")
def subscribe(sub: PushSubscription, db: Session = Depends(get_db)):
    """Store a push subscription (upsert by endpoint)."""
    ensure_table(db)
    db.execute(text("""
        INSERT INTO push_subscriptions (endpoint, p256dh, auth, topic)
        VALUES (:endpoint, :p256dh, :auth, :topic)
        ON CONFLICT (endpoint) DO UPDATE
            SET topic = EXCLUDED.topic,
                p256dh = EXCLUDED.p256dh,
                auth = EXCLUDED.auth
    """), {
        "endpoint": sub.endpoint,
        "p256dh": sub.keys.get("p256dh", ""),
        "auth": sub.keys.get("auth", ""),
        "topic": sub.topic,
    })
    db.commit()
    return {"status": "subscribed"}


@router.delete("/unsubscribe")
def unsubscribe(endpoint: str, db: Session = Depends(get_db)):
    """Remove a push subscription by endpoint URL."""
    ensure_table(db)
    db.execute(
        text("DELETE FROM push_subscriptions WHERE endpoint = :e"),
        {"e": endpoint}
    )
    db.commit()
    return {"status": "unsubscribed"}


@router.get("/stats")
def subscription_stats(db: Session = Depends(get_db)):
    """Return subscription count (admin use only)."""
    ensure_table(db)
    result = db.execute(text("SELECT COUNT(*) FROM push_subscriptions")).scalar()
    return {"total_subscriptions": result}
