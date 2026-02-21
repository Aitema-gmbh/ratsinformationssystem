import os
import anthropic

_client = None


def _get_client():
    global _client
    if _client is None and os.getenv("ANTHROPIC_API_KEY"):
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


async def generate_simple_language(full_text: str) -> str:
    """Generates a simple language (A2 level) version of a council paper."""
    client = _get_client()
    if not client:
        return full_text[:500] + "..." if len(full_text) > 500 else full_text

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": (
                    "Erklaere folgende Verwaltungsvorlage in einfacher Sprache (A2-Niveau):\n"
                    "- Kurze Saetze (max. 15 Woerter)\n"
                    "- Keine Fachbegriffe oder erklaeren falls noetig\n"
                    "- Aktive Sprache\n"
                    "- Max. 3 Absaetze\n\n"
                    "Vorlage:\n" + full_text[:3000]
                ),
            }],
        )
        return message.content[0].text
    except Exception as e:
        print(f"Simple language generation failed: {e}")
        return full_text[:500]
