"""
aitema|RIS - E-Mail-Service fuer Abonnement-Benachrichtigungen.

Unterstuetzt:
- Double-Opt-In Bestaetigungsmails
- Neue-Inhalte-Benachrichtigungen mit Digest-Schutz (24h)
- SMTP mit optionalem Login (STARTTLS)
"""
from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.subscription import Subscription

BASE_URL = os.getenv("BASE_URL", "https://ris.aitema.de")
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@aitema.de")


# -------------------------------------------------------------------
# Intern: SMTP senden
# -------------------------------------------------------------------

def _send_mail(to: str, subject: str, body_plain: str, body_html: str | None = None) -> None:
    """Sendet eine E-Mail via SMTP. Schlaegt bei Fehlern STILL fehl (kein App-Crash)."""
    try:
        if body_html:
            msg: MIMEMultipart | MIMEText = MIMEMultipart("alternative")
            msg.attach(MIMEText(body_plain, "plain", "utf-8"))
            msg.attach(MIMEText(body_html, "html", "utf-8"))
        else:
            msg = MIMEText(body_plain, "plain", "utf-8")

        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = to

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
            s.ehlo()
            try:
                s.starttls()
                s.ehlo()
            except Exception:
                pass  # localhost hat kein TLS
            if SMTP_USER:
                s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
    except Exception as exc:
        # Silent fail - E-Mail-Ausfall soll App nicht crashen
        print(f"[email_service] E-Mail-Fehler an {to}: {exc}")


# -------------------------------------------------------------------
# Double-Opt-In Bestaetigung
# -------------------------------------------------------------------

def send_confirmation_email(subscription: "Subscription") -> None:
    confirm_url = f"{BASE_URL}/api/v1/subscriptions/confirm/{subscription.confirm_token}"
    unsub_url = f"{BASE_URL}/api/v1/subscriptions/unsubscribe/{subscription.unsubscribe_token}"

    plain = f"""Guten Tag,

Sie haben ein Abonnement fuer \"{subscription.target_label}\" bei aitema|RIS angefragt.

Bitte bestaetigen Sie Ihr Abonnement mit folgendem Link:
{confirm_url}

Falls Sie diese Anfrage nicht gestellt haben, ignorieren Sie diese E-Mail bitte.
Der Link verfaellt nach 7 Tagen.

Sollten Sie sich abmelden wollen: {unsub_url}

-- 
aitema|RIS · Ratsinformationssystem
"""

    html = f"""<!DOCTYPE html>
<html lang="de">
<body style="font-family: sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; padding: 24px;">
  <div style="border-bottom: 2px solid #2563eb; padding-bottom: 12px; margin-bottom: 24px;">
    <strong style="color: #2563eb; font-size: 18px;">aitema|RIS</strong>
    <span style="color: #64748b; margin-left: 8px;">Ratsinformationssystem</span>
  </div>
  <h2 style="color: #1e293b;">Abonnement bestaetigen</h2>
  <p>Sie moechten Neuigkeiten zu <strong>{subscription.target_label}</strong> abonnieren.</p>
  <p>
    <a href="{confirm_url}" style="display: inline-block; background: #2563eb; color: #fff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600;">
      Abonnement bestaetigen
    </a>
  </p>
  <p style="color: #64748b; font-size: 14px;">Falls Sie diese Anfrage nicht gestellt haben, ignorieren Sie diese E-Mail.</p>
  <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
  <p style="color: #94a3b8; font-size: 12px;">
    <a href="{unsub_url}" style="color: #94a3b8;">Abmelden</a>
  </p>
</body>
</html>"""

    _send_mail(
        subscription.email,
        f"Bitte bestaetigen: Abonnement fuer {subscription.target_label}",
        plain,
        html,
    )


# -------------------------------------------------------------------
# Neue-Inhalte-Benachrichtigung
# -------------------------------------------------------------------

def send_new_item_notification(
    subscriptions: list["Subscription"],
    item_title: str,
    item_url: str,
    item_type: str = "Neue Meldung",
) -> None:
    """Benachrichtigt alle uebergebenen (bestaetigten) Abonnenten."""
    for sub in subscriptions:
        unsub_url = f"{BASE_URL}/api/v1/subscriptions/unsubscribe/{sub.unsubscribe_token}"

        plain = f"""Neue {item_type} zu \"{sub.target_label}\":

{item_title}
{item_url}

--
Abmelden: {unsub_url}
aitema|RIS · Ratsinformationssystem
"""

        html = f"""<!DOCTYPE html>
<html lang="de">
<body style="font-family: sans-serif; color: #1e293b; max-width: 600px; margin: 0 auto; padding: 24px;">
  <div style="border-bottom: 2px solid #2563eb; padding-bottom: 12px; margin-bottom: 24px;">
    <strong style="color: #2563eb;">aitema|RIS</strong>
  </div>
  <h2>Neue {item_type} zu <em>{sub.target_label}</em></h2>
  <p style="font-size: 16px;"><a href="{item_url}" style="color: #2563eb;">{item_title}</a></p>
  <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;">
  <p style="color: #94a3b8; font-size: 12px;">
    <a href="{unsub_url}" style="color: #94a3b8;">Abmelden</a>
  </p>
</body>
</html>"""

        _send_mail(sub.email, f"Neu: {item_title}", plain, html)
