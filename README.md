# aitema|RIS - OParl-First Ratsinformationssystem

Open-Source Ratsinformationssystem mit OParl 1.1 als Kernarchitektur.

## Architektur

- **Backend**: Python 3.12 / FastAPI / SQLAlchemy 2.0 (async)
- **Frontend**: React 18 / Next.js 14 (App Router, SSR)
- **Datenbank**: PostgreSQL 16 (Schema-per-Tenant)
- **Cache**: Redis 7
- **Suche**: Elasticsearch 8
- **Dokumente**: MinIO (S3-kompatibel)
- **Auth**: Keycloak (SSO, BundID)

## Schnellstart

```bash
# .env erstellen
cp .env.example .env

# Development-Umgebung starten
make dev

# Migrationen ausfuehren
make migrate

# Tests
make test
```

## OParl 1.1

Alle 12 OParl-Objekttypen sind implementiert:
System, Body, LegislativeTerm, Organization, Person, Membership,
Meeting, AgendaItem, Paper, Consultation, File, Location.

API-Einstiegspunkt: `GET /api/v1/oparl/system`

## Lizenz

EUPL-1.2 - European Union Public Licence
