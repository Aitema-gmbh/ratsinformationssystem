"""
aitema|RIS - Notification Service
Email notifications and WebSocket real-time updates.
"""
from __future__ import annotations

import json
from typing import Any, Optional

import structlog
from redis.asyncio import Redis

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


class NotificationService:
    """
    Service for sending notifications via email and WebSocket.
    Uses Redis PubSub for real-time WebSocket notifications.
    """

    def __init__(self) -> None:
        self.redis: Optional[Redis] = None

    async def connect(self) -> None:
        """Connect to Redis for PubSub."""
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()

    # --- Email Notifications ---

    async def send_email(
        self,
        to: str | list[str],
        subject: str,
        body_html: str,
        body_text: str | None = None,
    ) -> bool:
        """Send an email notification."""
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
            # In development, just log the email
            if settings.environment == "development":
                logger.info(
                    "Email (dev mode - not sent)",
                    to=to,
                    subject=subject,
                )
                return True

            # Production: send via SMTP
            await aiosmtplib.send(
                msg,
                hostname="localhost",
                port=25,
            )
            logger.info("Email sent", to=to, subject=subject)
            return True
        except Exception as e:
            logger.error("Email sending failed", to=to, error=str(e))
            return False

    async def send_meeting_invitation(
        self,
        meeting_name: str,
        meeting_date: str,
        recipients: list[str],
        body_name: str,
    ) -> None:
        """Send meeting invitation emails to all participants."""
        subject = f"Einladung: {meeting_name} - {body_name}"
        body_html = f"""
        <html>
        <body>
            <h2>Einladung zur Sitzung</h2>
            <p><strong>{meeting_name}</strong></p>
            <p>Datum: {meeting_date}</p>
            <p>Koerperschaft: {body_name}</p>
            <p>
                Die Tagesordnung und alle zugehoerigen Unterlagen finden Sie im
                Ratsinformationssystem.
            </p>
        </body>
        </html>
        """
        await self.send_email(recipients, subject, body_html)

    async def send_workflow_notification(
        self,
        paper_name: str,
        step_name: str,
        action: str,
        recipient: str,
    ) -> None:
        """Send workflow step notification."""
        action_text = {
            "submitted": "wurde zur Freigabe eingereicht",
            "approved": "wurde genehmigt",
            "rejected": "wurde abgelehnt",
            "returned": "wurde zurueckgegeben",
        }.get(action, action)

        subject = f"Workflow: {paper_name} - {action_text}"
        body_html = f"""
        <html>
        <body>
            <h2>Workflow-Benachrichtigung</h2>
            <p>Die Vorlage <strong>{paper_name}</strong> {action_text}.</p>
            <p>Aktueller Schritt: {step_name}</p>
        </body>
        </html>
        """
        await self.send_email(recipient, subject, body_html)

    # --- WebSocket / PubSub Notifications ---

    async def publish_event(
        self,
        channel: str,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        """Publish a real-time event via Redis PubSub."""
        if not self.redis:
            await self.connect()

        message = json.dumps({
            "type": event_type,
            "data": data,
        })

        try:
            await self.redis.publish(channel, message)
            logger.debug("Event published", channel=channel, type=event_type)
        except Exception as e:
            logger.error("Event publish failed", error=str(e))

    async def publish_meeting_update(
        self,
        body_id: str,
        meeting_id: str,
        action: str,
    ) -> None:
        """Publish a meeting update event."""
        await self.publish_event(
            channel=f"body:{body_id}:meetings",
            event_type="meeting_update",
            data={"meeting_id": meeting_id, "action": action},
        )

    async def publish_paper_update(
        self,
        body_id: str,
        paper_id: str,
        action: str,
    ) -> None:
        """Publish a paper update event."""
        await self.publish_event(
            channel=f"body:{body_id}:papers",
            event_type="paper_update",
            data={"paper_id": paper_id, "action": action},
        )

    async def subscribe(self, channel: str):
        """Subscribe to a Redis PubSub channel (for WebSocket consumers)."""
        if not self.redis:
            await self.connect()

        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
