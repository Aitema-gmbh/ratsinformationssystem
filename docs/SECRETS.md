# Secrets und Konfiguration – aitema|Rats

## Schnellstart

```bash
# Template kopieren und anpassen
cp .env.production.example .env.production
nano .env.production
```

## Sichere Passwörter generieren

```bash
# 32-Byte Hex Secret (für Passwörter, Schlüssel)
openssl rand -hex 32

# 64-Byte Hex Secret (für SECRET_KEY)
openssl rand -hex 64

# UUID (alternative)
uuidgen
```

## Pflichtfelder

| Variable | Beschreibung | Generierung |
|----------|-------------|-------------|
| `POSTGRES_PASSWORD` | Datenbank-Passwort | `openssl rand -hex 32` |
| `REDIS_PASSWORD` | Redis-Passwort | `openssl rand -hex 32` |
| `ES_PASSWORD` | Elasticsearch-Passwort | `openssl rand -hex 32` |
| `MINIO_SECRET_KEY` | MinIO-Zugriffsschlüssel | `openssl rand -hex 32` |
| `KEYCLOAK_ADMIN_PASSWORD` | Keycloak-Admin-Passwort | `openssl rand -hex 32` |
| `SECRET_KEY` | Haupt-Session-Secret (min. 64 Zeichen) | `openssl rand -hex 64` |
| `CORS_ORIGINS` | Erlaubte Frontend-URL(s) | z.B. `https://ris.example.de` |
| `PUBLIC_API_URL` | Öffentliche API-URL | z.B. `https://ris.example.de/api` |
| `OPARL_BODY_ID` | OParl-Körperschaft-ID | z.B. `https://ris.example.de/api/oparl/v1.1/body/1` |

## OParl-Konfiguration

Das RIS implementiert die OParl 1.1 Schnittstelle. Die folgenden Werte
müssen mit den tatsächlichen URLs Ihrer Instanz übereinstimmen:

| Variable | Beispiel |
|----------|---------|
| `OPARL_BODY_ID` | `https://ris.meine-kommune.de/api/oparl/v1.1/body/1` |
| `OPARL_SYSTEM_URL` | `https://ris.meine-kommune.de/api/oparl/v1.1/system` |

Weitere Informationen: `docs/OPARL_MAPPING.md`

## Keycloak SSO-Einrichtung

1. Keycloak-Admin-Konsole aufrufen: `https://sso.IHRE-DOMAIN.de`
2. Realm `ris` erstellen
3. Client `ris-frontend` anlegen (öffentlicher Client, PKCE aktivieren)
4. Rollen anlegen: `ris-admin`, `ris-redakteur`, `ris-leser`

## GitHub Actions Secrets

Für CI/CD müssen folgende Secrets in GitHub unter
`Settings → Secrets → Actions` hinterlegt werden:

| Secret | Beschreibung |
|--------|-------------|
| `GHCR_TOKEN` | GitHub Container Registry Token (ghcr.io) |
| `DEPLOY_SSH_KEY` | SSH-Private-Key für den Deployment-Server |
| `DEPLOY_HOST` | IP oder Hostname des Deployment-Servers |
| `POSTGRES_PASSWORD_PROD` | Produktions-Datenbank-Passwort |
| `ES_PASSWORD_PROD` | Elasticsearch-Produktions-Passwort |
| `MINIO_SECRET_KEY_PROD` | MinIO-Produktions-Schlüssel |
| `KEYCLOAK_ADMIN_PASSWORD_PROD` | Keycloak-Admin-Passwort |
| `SECRET_KEY_PROD` | Produktions-Session-Secret |
| `SENTRY_DSN` | Sentry-DSN für Error-Tracking (optional) |

## .gitignore (wichtig\!)

Stelle sicher, dass `.env.production` in `.gitignore` eingetragen ist:

```
.env
.env.*
\!.env*.example
\!.env.prod.example
\!.env.production.example
```

## Sicherheitshinweise

- **Rotation**: Ändere alle Secrets bei Verdacht auf Kompromittierung sofort
- **Backup**: Sichere `.env.production` verschlüsselt außerhalb des Repos
- **Keycloak**: Deaktiviere den Keycloak-Master-Realm nach Ersteinrichtung
- **MinIO**: Aktiviere Server-Side-Encryption für Dokument-Buckets
- Melde Sicherheitslücken gemäß `/SECURITY.md`
