"""
aitema|RIS - Subscriptions Router

D5 Buerger-Abonnement fuer Gremien/Themen.

Endpunkte:
  POST   /api/v1/subscriptions/            - Abonnement anlegen (Double-Opt-In)
  GET    /api/v1/subscriptions/confirm/{token}     - E-Mail bestaetigen
  GET    /api/v1/subscriptions/unsubscribe/{token} - Abmelden (DSGVO)
  GET    /api/v1/subscriptions/status      - Eigene Abos abfragen (per E-Mail-Token)
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.subscription import Subscription
from app.services.email_service import send_confirmation_email

router = APIRouter(prefix="/api/v1/subscriptions", tags=["Abonnements"])

BASE_URL = __import__("os").getenv("BASE_URL", "https://ris.aitema.de")
MAX_SUBSCRIPTIONS_PER_EMAIL = 10  # Rate-Limit: max. Abos pro E-Mail


# -------------------------------------------------------------------
# Pydantic Schemas
# -------------------------------------------------------------------

VALID_TYPES = {"organization", "keyword", "meeting_calendar"}


class SubscribeRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        import re
        v = v.strip().lower()
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", v):
            raise ValueError("Ungueltige E-Mail-Adresse")
        return v
    subscription_type: str
    target_id: str
    target_label: str

    @field_validator("subscription_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in VALID_TYPES:
            raise ValueError(f"subscription_type muss einer von {VALID_TYPES} sein")
        return v

    @field_validator("target_id", "target_label")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Darf nicht leer sein")
        return v.strip()[:255]


class SubscribeResponse(BaseModel):
    message: str
    subscription_id: Optional[str] = None


# -------------------------------------------------------------------
# POST /  → Abonnement anlegen
# -------------------------------------------------------------------

@router.post("/", response_model=SubscribeResponse, status_code=201)
async def subscribe(
    payload: SubscribeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> SubscribeResponse:
    """
    Legt ein neues Abonnement an und sendet eine Bestaetigunsmail.
    Rate-Limit: max. 10 aktive Abonnements pro E-Mail-Adresse.
    Duplikat-Schutz: kein zweites Abo fuer exakt gleiche Kombination.
    """
    # Duplikat-Pruefung
    existing = (
        db.query(Subscription)
        .filter(
            Subscription.email == payload.email,
            Subscription.subscription_type == payload.subscription_type,
            Subscription.target_id == payload.target_id,
        )
        .first()
    )
    if existing:
        if existing.confirmed:
            raise HTTPException(409, detail="Dieses Abonnement existiert bereits.")
        # Noch unbestaetigt → erneut Bestaetigunsmail senden
        background_tasks.add_task(send_confirmation_email, existing)
        return SubscribeResponse(
            message="Bestaetigunsmail erneut gesendet.",
            subscription_id=existing.id,
        )

    # Rate-Limit
    active_count = (
        db.query(Subscription)
        .filter(Subscription.email == payload.email)
        .count()
    )
    if active_count >= MAX_SUBSCRIPTIONS_PER_EMAIL:
        raise HTTPException(
            429,
            detail=f"Maximal {MAX_SUBSCRIPTIONS_PER_EMAIL} Abonnements pro E-Mail-Adresse erlaubt.",
        )

    sub = Subscription(
        email=payload.email,
        subscription_type=payload.subscription_type,
        target_id=payload.target_id,
        target_label=payload.target_label,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    background_tasks.add_task(send_confirmation_email, sub)

    return SubscribeResponse(
        message="Bitte bestaetigen Sie Ihr Abonnement per E-Mail.",
        subscription_id=sub.id,
    )


# -------------------------------------------------------------------
# GET /confirm/{token}  → E-Mail bestaetigen
# -------------------------------------------------------------------

_CONFIRM_SUCCESS_HTML = """<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><title>Abonnement bestätigt – aitema|RIS</title></head>
<body style="font-family:sans-serif;max-width:520px;margin:60px auto;text-align:center;color:#1e293b">
  <div style="font-size:64px;margin-bottom:16px">✅</div>
  <h1 style="color:#1e293b">Abonnement bestätigt!</h1>
  <p style="color:#475569">Sie erhalten ab sofort E-Mail-Benachrichtigungen.</p>
  <a href="{base_url}" style="display:inline-block;margin-top:24px;background:#2563eb;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:600">Zur Startseite</a>
</body>
</html>"""

_CONFIRM_ERROR_HTML = """<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><title>Ungültiger Link – aitema|RIS</title></head>
<body style="font-family:sans-serif;max-width:520px;margin:60px auto;text-align:center;color:#1e293b">
  <div style="font-size:64px;margin-bottom:16px">❌</div>
  <h1>Ungültiger oder abgelaufener Link</h1>
  <p style="color:#475569">Bitte starten Sie den Abonnement-Prozess erneut.</p>
  <a href="{base_url}" style="display:inline-block;margin-top:24px;background:#64748b;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none">Zur Startseite</a>
</body>
</html>"""


@router.get("/confirm/{token}", response_class=HTMLResponse)
def confirm_subscription(token: str, db: Session = Depends(get_db)) -> HTMLResponse:
    """Bestaetigt ein Abonnement via Token aus der Bestaetigunsmail."""
    sub = db.query(Subscription).filter(Subscription.confirm_token == token).first()
    if not sub:
        return HTMLResponse(
            _CONFIRM_ERROR_HTML.format(base_url=BASE_URL), status_code=404
        )
    sub.confirmed = True
    db.commit()
    return HTMLResponse(_CONFIRM_SUCCESS_HTML.format(base_url=BASE_URL), status_code=200)


# -------------------------------------------------------------------
# GET /unsubscribe/{token}  → Abmelden (DSGVO)
# -------------------------------------------------------------------

_UNSUB_SUCCESS_HTML = """<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><title>Abgemeldet – aitema|RIS</title></head>
<body style="font-family:sans-serif;max-width:520px;margin:60px auto;text-align:center;color:#1e293b">
  <div style="font-size:64px;margin-bottom:16px">👋</div>
  <h1>Erfolgreich abgemeldet</h1>
  <p style="color:#475569">Ihr Abonnement wurde geloescht. Sie erhalten keine weiteren E-Mails.</p>
  <a href="{base_url}" style="display:inline-block;margin-top:24px;background:#64748b;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none">Zur Startseite</a>
</body>
</html>"""

_UNSUB_ERROR_HTML = """<!DOCTYPE html>
<html lang="de">
<head><meta charset="UTF-8"><title>Ungültiger Link – aitema|RIS</title></head>
<body style="font-family:sans-serif;max-width:520px;margin:60px auto;text-align:center;color:#1e293b">
  <div style="font-size:64px;margin-bottom:16px">❌</div>
  <h1>Ungültiger Abmelde-Link</h1>
  <p style="color:#475569">Moeglicherweise wurde dieses Abonnement bereits geloescht.</p>
  <a href="{base_url}" style="display:inline-block;margin-top:24px;background:#64748b;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none">Zur Startseite</a>
</body>
</html>"""


@router.get("/unsubscribe/{token}", response_class=HTMLResponse)
def unsubscribe(token: str, db: Session = Depends(get_db)) -> HTMLResponse:
    """Loescht ein Abonnement via Token (DSGVO-konformes Hard-Delete)."""
    sub = db.query(Subscription).filter(Subscription.unsubscribe_token == token).first()
    if not sub:
        return HTMLResponse(
            _UNSUB_ERROR_HTML.format(base_url=BASE_URL), status_code=404
        )
    db.delete(sub)
    db.commit()
    return HTMLResponse(_UNSUB_SUCCESS_HTML.format(base_url=BASE_URL), status_code=200)


# -------------------------------------------------------------------
# Hilfsfunktion fuer andere Router: Passende Abonnenten finden
# -------------------------------------------------------------------

def get_subscribers_for_organization(
    db: Session,
    organization_id: str,
    min_digest_hours: int = 24,
) -> list[Subscription]:
    """
    Gibt bestaetigte Abonnenten zurueck, die fuer eine Organisation abonniert haben
    und in den letzten  Stunden noch keine Benachrichtigung erhalten haben.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=min_digest_hours)
    return (
        db.query(Subscription)
        .filter(
            Subscription.subscription_type == "organization",
            Subscription.target_id == organization_id,
            Subscription.confirmed == True,  # noqa: E712
            (Subscription.last_notified_at == None)  # noqa: E711
            | (Subscription.last_notified_at < cutoff),
        )
        .all()
    )


def get_subscribers_for_keyword(
    db: Session,
    keyword: str,
    min_digest_hours: int = 24,
) -> list[Subscription]:
    """Gibt bestaetigte Keyword-Abonnenten zurueck (Digest-Schutz)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=min_digest_hours)
    return (
        db.query(Subscription)
        .filter(
            Subscription.subscription_type == "keyword",
            Subscription.target_id == keyword,
            Subscription.confirmed == True,  # noqa: E712
            (Subscription.last_notified_at == None)  # noqa: E711
            | (Subscription.last_notified_at < cutoff),
        )
        .all()
    )
