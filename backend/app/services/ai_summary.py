import os
import logging

logger = logging.getLogger(__name__)


async def generate_paper_summary(full_text: str) -> str:
    """
    Generiert eine 2-saetzige Zusammenfassung einer Verwaltungsvorlage.
    Fallback auf Text-Kuerzung wenn kein ANTHROPIC_API_KEY gesetzt.
    """
    if not full_text or not full_text.strip():
        return ""

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.info("ANTHROPIC_API_KEY nicht gesetzt - Fallback auf Text-Kuerzung")
        return _text_fallback(full_text)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    "Fasse folgende Verwaltungsvorlage in genau 2 Saetzen zusammen. "
                    "Neutral, sachlich, kein Fachjargon, verstaendlich fuer alle Buerger:\n\n"
                    + full_text[:4000]
                ),
            }]
        )
        return message.content[0].text.strip()

    except ImportError:
        logger.warning("anthropic-Paket nicht installiert - Fallback")
        return _text_fallback(full_text)
    except Exception as e:
        logger.error("KI-Zusammenfassung fehlgeschlagen: %s", e)
        return _text_fallback(full_text)


def _text_fallback(text: str, max_chars: int = 300) -> str:
    """Einfache Text-Kuerzung als Fallback ohne KI."""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    last_period = max(truncated.rfind(". "), truncated.rfind(".\n"))
    if last_period > max_chars // 2:
        return truncated[:last_period + 1]
    return truncated + "..."
