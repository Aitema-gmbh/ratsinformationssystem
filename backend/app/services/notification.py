"""
aitema|RIS - Benachrichtigungs-Service

Verwaltet Abonnements und versendet Benachrichtigungen:
- subscribe_topic() - Buerger/Mandatstraeger zu Thema/Gremium subscriben
- notify_new_paper() - Neue Vorlage veroeffentlicht
- notify_meeting_scheduled() - Neue Sitzung angesetzt
- notify_decision() - Beschluss gefasst
- send_email() - E-Mail via SMTP
- send_push() - Web Push Notification (Placeholder)
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

import structlog
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database import get_session

settings = get_settings()
logger = structlog.get_logger()


# ============================================================
# Subscription-Typen
# ============================================================
SUBSCRIPTION_TYPES = [
    "body",           # Alle Neuigkeiten einer Koerperschaft
    "organization",   # Fraktion/Ausschuss
    "paper_type",     # Vorlagen-Typ (Antrag, Beschlussvorlage, etc.)
    "keyword",        # Schlagwort/Thema
    "person",         # Mandatstraeger
]


class NotificationService:
    """
    Benachrichtigungs-Service fuer Abonnements, E-Mails und Push-Nachrichten.
    Nutzt Redis fuer PubSub und Subscription-Speicherung.
    """

    def __init__(self) -> None:
        self.redis: Optional[Redis] = None

    async def connect(self) -> None:
        """Mit Redis verbinden."""
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    async def disconnect(self) -> None:
        """Redis-Verbindung trennen."""
        if self.redis:
            await self.redis.close()

    async def _ensure_redis(self) -> None:
        if not self.redis:
            await self.connect()

    # ========================================
    # Abonnement-Verwaltung
    # ========================================

    async def subscribe_topic(
        self,
        user_email: str,
        subscription_type: str,
        topic_id: str,
        tenant: str = "public",
        channels: list[str] | None = None,
    ) -> dict:
        """
        Buerger oder Mandatstraeger fuer ein Thema/Gremium subscriben.

        Args:
            user_email: E-Mail-Adresse des Abonnenten
            subscription_type: body, organization, paper_type, keyword, person
            topic_id: ID des abonnierten Objekts
            tenant: Mandant
            channels: Benachrichtigungskanaele ["email", "push"]

        Returns:
            Subscription-Objekt
        """
        await self._ensure_redis()

        if subscription_type not in SUBSCRIPTION_TYPES:
            raise ValueError(
                f"Ungueltiger Typ: {subscription_type}. "
                f"Erlaubt: {SUBSCRIPTION_TYPES}"
            )

        if channels is None:
            channels = ["email"]

        sub_key = f"sub:{tenant}:{subscription_type}:{topic_id}"
        sub_data = json.dumps({
            "email": user_email,
            "type": subscription_type,
            "topic_id": topic_id,
            "tenant": tenant,
            "channels": channels,
            "subscribed_at": datetime.utcnow().isoformat(),
        })

        await self.redis.sadd(sub_key, sub_data)

        # Reverse-Index: User -> Subscriptions
        user_key = f"user_subs:{user_email}"
        await self.redis.sadd(user_key, f"{subscription_type}:{topic_id}")

        logger.info(
            "Abonnement erstellt",
            email=user_email,
            type=subscription_type,
            topic=topic_id,
        )

        return {
            "email": user_email,
            "type": subscription_type,
            "topic_id": topic_id,
            "channels": channels,
        }

    async def unsubscribe_topic(
        self,
        user_email: str,
        subscription_type: str,
        topic_id: str,
        tenant: str = "public",
    ) -> bool:
        """Abonnement entfernen."""
        await self._ensure_redis()

        sub_key = f"sub:{tenant}:{subscription_type}:{topic_id}"
        members = await self.redis.smembers(sub_key)

        for member in members:
            data = json.loads(member)
            if data["email"] == user_email:
                await self.redis.srem(sub_key, member)
                user_key = f"user_subs:{user_email}"
                await self.redis.srem(user_key, f"{subscription_type}:{topic_id}")
                logger.info("Abonnement entfernt", email=user_email, topic=topic_id)
                return True
        return False

    async def get_subscribers(
        self,
        subscription_type: str,
        topic_id: str,
        tenant: str = "public",
    ) -> list[dict]:
        """Alle Abonnenten fuer ein Thema abrufen."""
        await self._ensure_redis()

        sub_key = f"sub:{tenant}:{subscription_type}:{topic_id}"
        members = await self.redis.smembers(sub_key)

        return [json.loads(m) for m in members]

    # ========================================
    # Benachrichtigungen versenden
    # ========================================

    async def notify_new_paper(
        self,
        paper_name: str,
        paper_reference: str,
        paper_type: str,
        body_id: str,
        body_name: str,
        paper_url: str,
        tenant: str = "public",
    ) -> int:
        """
        Benachrichtigung: Neue Vorlage veroeffentlicht.
        Benachrichtigt Abonnenten von body und paper_type.
        """
        # Body-Abonnenten
        body_subs = await self.get_subscribers("body", body_id, tenant)
        # Paper-Typ-Abonnenten
        type_subs = await self.get_subscribers("paper_type", paper_type, tenant)

        # Deduplizieren nach E-Mail
        all_emails = {s["email"] for s in body_subs + type_subs}

        subject = f"Neue Vorlage: {paper_reference} - {paper_name}"
        body_html = f"""
        <html>
        <body style="font-family: sans-serif;">
            <h2>Neue Vorlage im Ratsinformationssystem</h2>
            <table style="border-collapse: collapse; margin: 1rem 0;">
                <tr><td style="padding: 0.5rem; color: #6b7280;">Aktenzeichen:</td>
                    <td style="padding: 0.5rem; font-weight: 600;">{paper_reference}</td></tr>
                <tr><td style="padding: 0.5rem; color: #6b7280;">Titel:</td>
                    <td style="padding: 0.5rem;">{paper_name}</td></tr>
                <tr><td style="padding: 0.5rem; color: #6b7280;">Typ:</td>
                    <td style="padding: 0.5rem;">{paper_type}</td></tr>
                <tr><td style="padding: 0.5rem; color: #6b7280;">Koerperschaft:</td>
                    <td style="padding: 0.5rem;">{body_name}</td></tr>
            </table>
            <p><a href="{paper_url}">Vorlage im RIS ansehen</a></p>
        </body>
        </html>
        """

        sent = 0
        for email in all_emails:
            ok = await self.send_email(email, subject, body_html)
            if ok:
                sent += 1

        # Push-Benachrichtigung
        await self.send_push(
            title=f"Neue Vorlage: {paper_reference}",
            body=paper_name,
            url=paper_url,
            topic_type="body",
            topic_id=body_id,
            tenant=tenant,
        )

        logger.info("Benachrichtigung neue Vorlage", paper=paper_reference, sent=sent)
        return sent

    async def notify_meeting_scheduled(
        self,
        meeting_name: str,
        meeting_date: str,
        organization_id: str,
        organization_name: str,
        body_id: str,
        body_name: str,
        meeting_url: str,
        tenant: str = "public",
    ) -> int:
        """Benachrichtigung: Neue Sitzung angesetzt."""
        body_subs = await self.get_subscribers("body", body_id, tenant)
        org_subs = await self.get_subscribers("organization", organization_id, tenant)

        all_emails = {s["email"] for s in body_subs + org_subs}

        subject = f"Sitzung: {meeting_name} am {meeting_date}"
        body_html = f"""
        <html>
        <body style="font-family: sans-serif;">
            <h2>Neue Sitzung angesetzt</h2>
            <p><strong>{meeting_name}</strong></p>
            <table style="border-collapse: collapse; margin: 1rem 0;">
                <tr><td style="padding: 0.5rem; color: #6b7280;">Datum:</td>
                    <td style="padding: 0.5rem; font-weight: 600;">{meeting_date}</td></tr>
                <tr><td style="padding: 0.5rem; color: #6b7280;">Gremium:</td>
                    <td style="padding: 0.5rem;">{organization_name}</td></tr>
                <tr><td style="padding: 0.5rem; color: #6b7280;">Koerperschaft:</td>
                    <td style="padding: 0.5rem;">{body_name}</td></tr>
            </table>
            <p><a href="{meeting_url}">Sitzung im RIS ansehen</a></p>
        </body>
        </html>
        """

        sent = 0
        for email in all_emails:
            ok = await self.send_email(email, subject, body_html)
            if ok:
                sent += 1

        logger.info("Benachrichtigung Sitzung", meeting=meeting_name, sent=sent)
        return sent

    async def notify_decision(
        self,
        paper_name: str,
        paper_reference: str,
        decision_text: str,
        meeting_name: str,
        body_id: str,
        body_name: str,
        paper_url: str,
        tenant: str = "public",
    ) -> int:
        """Benachrichtigung: Beschluss gefasst."""
        body_subs = await self.get_subscribers("body", body_id, tenant)

        all_emails = {s["email"] for s in body_subs}

        subject = f"Beschluss: {paper_reference} - {paper_name}"
        body_html = f"""
        <html>
        <body style="font-family: sans-serif;">
            <h2>Beschluss gefasst</h2>
            <table style="border-collapse: collapse; margin: 1rem 0;">
                <tr><td style="padding: 0.5rem; color: #6b7280;">Vorlage:</td>
                    <td style="padding: 0.5rem;">{paper_reference} - {paper_name}</td></tr>
                <tr><td style="padding: 0.5rem; color: #6b7280;">Sitzung:</td>
                    <td style="padding: 0.5rem;">{meeting_name}</td></tr>
                <tr><td style="padding: 0.5rem; color: #6b7280;">Beschluss:</td>
                    <td style="padding: 0.5rem; font-weight: 600;">{decision_text}</td></tr>
            </table>
            <p><a href="{paper_url}">Details im RIS ansehen</a></p>
        </body>
        </html>
        """

        sent = 0
        for email in all_emails:
            ok = await self.send_email(email, subject, body_html)
            if ok:
                sent += 1

        logger.info("Benachrichtigung Beschluss", paper=paper_reference, sent=sent)
        return sent

    # ========================================
    # E-Mail-Versand
    # ========================================

    async def send_email(
        self,
        to: str | list[str],
        subject: str,
        body_html: str,
        body_text: str | None = None,
    ) -> bool:
        """E-Mail via SMTP versenden."""
        import aiosmtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        if isinstance(to, str):
            to = [to]

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.app_name} <noreply@aitema.de>"
        msg["To"] = ", ".join(to)

        if body_text:
            msg.attach(MIMEText(body_text, "plain", "utf-8"))
        msg.attach(MIMEText(body_html, "html", "utf-8"))

        try:
            if settings.environment == "development":
                logger.info("E-Mail (Dev-Modus)", to=to, subject=subject)
                return True

            await aiosmtplib.send(msg, hostname="localhost", port=25)
            logger.info("E-Mail gesendet", to=to, subject=subject)
            return True
        except Exception as e:
            logger.error("E-Mail-Versand fehlgeschlagen", to=to, error=str(e))
            return False

    # ========================================
    # Web Push (Placeholder)
    # ========================================

    async def send_push(
        self,
        title: str,
        body: str,
        url: str,
        topic_type: str,
        topic_id: str,
        tenant: str = "public",
    ) -> int:
        """
        Web Push Notification an alle Abonnenten senden.
        Placeholder - erfordert Push-Subscription-Registrierung im Frontend.
        """
        await self._ensure_redis()

        subscribers = await self.get_subscribers(topic_type, topic_id, tenant)
        push_subs = [s for s in subscribers if "push" in s.get("channels", [])]

        if not push_subs:
            return 0

        # PubSub-Event fuer WebSocket-basierte Push-Benachrichtigung
        push_payload = json.dumps({
            "type": "push_notification",
            "data": {
                "title": title,
                "body": body,
                "url": url,
                "timestamp": datetime.utcnow().isoformat(),
            },
        })

        channel = f"push:{tenant}:{topic_type}:{topic_id}"
        await self.redis.publish(channel, push_payload)

        logger.info(
            "Push-Benachrichtigung gesendet",
            title=title,
            subscribers=len(push_subs),
        )
        return len(push_subs)

    # ========================================
    # PubSub (fuer Echtzeit-Updates)
    # ========================================

    async def publish_event(
        self,
        channel: str,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        """Echtzeit-Event ueber Redis PubSub publizieren."""
        await self._ensure_redis()

        message = json.dumps({
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        })

        try:
            await self.redis.publish(channel, message)
            logger.debug("Event publiziert", channel=channel, type=event_type)
        except Exception as e:
            logger.error("Event-Publish fehlgeschlagen", error=str(e))

    async def subscribe(self, channel: str):
        """Redis PubSub Channel abonnieren (fuer WebSocket-Consumer)."""
        await self._ensure_redis()
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
