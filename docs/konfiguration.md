# Konfiguration – aitema|Rats RIS

Alle Konfigurationsoptionen werden über Umgebungsvariablen in der Datei `.env` gesetzt.
Die Vorlage befindet sich in `.env.example` im Wurzelverzeichnis des Projekts.

## Pflichtfelder

| Variable | Beschreibung |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL-Verbindungsstring |
| `NEXT_PUBLIC_BASE_URL` | Öffentliche URL der Anwendung |

## OParl-Schnittstelle

Das RIS unterstützt die OParl-API (Version 1.1) für den Datenaustausch mit anderen
Ratsinformationssystemen und für den Import externer Daten:

```env
OPARL_API_URL=https://ris.andere-gemeinde.de/oparl/v1.1
OPARL_API_KEY=optionaler_api_schluessel
```

Das eigene OParl-Endpunkt ist unter `{BASE_URL}/oparl/v1.1` erreichbar.

## Cache-Einstellungen

```env
# Seiteninhalt 5 Minuten cachen (empfohlen für öffentliche Ansicht)
CACHE_TTL_SECONDS=300

# Cache deaktivieren (nur für Entwicklung)
# CACHE_TTL_SECONDS=0
```

## Volltext-Suche

```env
# Aktiviert (Standard)
ENABLE_FULLTEXT_SEARCH=true

# Nach Aktivierung Index aufbauen:
# docker compose exec backend python manage.py rebuild_index
```

## Weitere Informationen

Siehe auch:
- [Installation](installation.md)
- [FAQ](faq.md)
- [OParl-Mapping](OPARL_MAPPING.md)
