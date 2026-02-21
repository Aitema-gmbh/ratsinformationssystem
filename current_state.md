# Current State: aitema|RIS (Ratsinformationssystem)
**Stand:** 2026-02-20
**Status:** Live (alle Seiten erreichbar, API Health-Endpunkt fehlt)

## Live URLs
- Frontend: https://ris.aitema.de
- Suche: https://ris.aitema.de/suche (Haupt-Einstiegsseite via Redirect)
- Sitzungen: https://ris.aitema.de/sitzungen
- API Docs: https://ris.aitema.de/api/docs

## Container Status

| Container | Image | Status |
|-----------|-------|--------|
| ris-frontend | aitema-ris-frontend:latest | Up (healthy) |
| ris-backend | aitema-ris-backend:latest | Up |
| ris-postgres | postgres:16-alpine | Up (healthy) |
| ris-redis | redis:7-alpine | Up (healthy) |

## Letzter Deployment
- Datum: 2026-02-20
- Methode: Docker Compose + Traefik
- Frontend: Next.js auf Port 3000
- Backend: FastAPI/Uvicorn auf Port 8000
- Stack-Verzeichnis: /opt/aitema/ratsinformationssystem/

## Bekannte Issues

### /api/health gibt 404 zurueck
- GET https://ris.aitema.de/api/health -> 404 Not Found
- GET https://ris.aitema.de/api/v1/health -> 404 Not Found
- Das Backend hat keinen dedizierten /health Endpunkt
- Backend-Logs: GET /api/ -> 307 Temporary Redirect
- Fix: Health-Endpoint im FastAPI-Backend hinzufuegen

### SyntaxWarning im Backend-Code
- /app/app/services/calendar.py:19: SyntaxWarning: invalid escape sequence
- Zeile: text.replace(";", "\;") -> kein funktionaler Fehler, aber Code-Qualitaetsproblem

### Root-Redirect Status
- https://ris.aitema.de/ -> 302 Redirect -> /suche
- Koennte auf 301 permanent umgestellt werden

## Naechste Schritte
1. Health-Endpoint zum FastAPI-Backend hinzufuegen (GET /api/health -> 200)
2. SyntaxWarning in calendar.py beheben
3. Root-Redirect auf 301 permanent umstellen
4. Sitzungsdaten befuellen und E2E-Tests durchfuehren

## Technischer Stack
- Frontend: Next.js (aitema-ris-frontend:latest, Port 3000)
- Backend: FastAPI + Uvicorn (aitema-ris-backend:latest, Port 8000)
- Datenbank: PostgreSQL 16 Alpine (Locale: de_DE.UTF-8)
- Cache: Redis 7 Alpine
- Reverse Proxy: Traefik v3.6 + Cloudflare Origin Cert
- TLS: Cloudflare Origin Certificate (gueltig bis 2041)

## Healthcheck URLs
- https://ris.aitema.de/ -> HTTP 200 (via Redirect zu /suche)
- https://ris.aitema.de/suche -> HTTP 200 OK
- https://ris.aitema.de/sitzungen -> HTTP 200 OK
- https://ris.aitema.de/api/health -> HTTP 404 (Endpunkt fehlt - BUG)
- https://ris.aitema.de/api/docs -> HTTP 200 (Swagger UI verfuegbar)

## HTTP->HTTPS Redirect
- http://ris.aitema.de/ -> 301 -> https://ris.aitema.de/ (korrekt via Traefik)
