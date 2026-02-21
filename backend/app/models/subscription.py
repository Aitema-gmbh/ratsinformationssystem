"""
aitema|RIS - Subscription Model

D5 Buerger-Abonnement fuer Gremien/Themen.
Double-Opt-In, DSGVO-konform, Digest-fähig.
"""
from __future__ import annotations

import secrets
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Subscription(Base):
    """Buerger-Abonnement fuer Gremien oder Stichwörter."""
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
        default=lambda: secrets.token_urlsafe(16),
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subscription_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
        doc="'organization' | 'keyword' | 'meeting_calendar'"
    )
    target_id: Mapped[str] = mapped_column(
        String(255), nullable=False,
        doc="organization_id, keyword-slug oder 'all'"
    )
    target_label: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
        doc="Menschenlesbarer Anzeigename"
    )
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confirm_token: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False,
        default=lambda: secrets.token_urlsafe(32),
    )
    unsubscribe_token: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False,
        default=lambda: secrets.token_urlsafe(32),
    )
    last_notified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
