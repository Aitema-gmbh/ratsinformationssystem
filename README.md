<div align="center">

# aitema|Rats

**OParl-First Ratsinformationssystem fuer deutsche Kommunen**

[![CI](https://github.com/aitema-gmbh/ratsinformationssystem/actions/workflows/ci.yml/badge.svg)](https://github.com/aitema-gmbh/ratsinformationssystem/actions/workflows/ci.yml)
[![License: EUPL-1.2](https://img.shields.io/badge/License-EUPL--1.2-blue.svg)](https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12)
[![OParl 1.1](https://img.shields.io/badge/OParl-1.1-green.svg)](https://oparl.org)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-000000.svg)](https://nextjs.org)

*Open-Source-Ratsinformationssystem basierend auf dem OParl-1.1-Standard.*
*Entwickelt fuer die besonderen Anforderungen deutscher Kommunalverwaltungen.*

[Schnellstart](#schnellstart) | [API-Dokumentation](#oparl-11-api) | [Demo](https://demo.rats.aitema.de) | [Kontakt](#kontakt)

</div>

---

## Ueberblick

**aitema|Rats** ist ein modernes, quelloffenes Ratsinformationssystem (RIS), das den
[OParl-1.1-Standard](https://oparl.org) als Kernarchitektur verwendet. Es ermoeglicht
Kommunen die transparente Verwaltung und Bereitstellung parlamentarischer Informationen
und bietet sowohl eine leistungsfaehige Verwaltungsoberflaeche als auch ein
oeffentliches Buergerportal.

### Warum aitema|Rats?

- **OParl-nativ**: Kein nachtraegliches API-Addon -- OParl 1.1 ist die Kernarchitektur
- **Open Source**: EUPL-1.2-Lizenz, kein Vendor Lock-in
- **Modern**: Aktuelle Technologien statt Legacy-Software aus den 2000ern
- **Migrierbar**: Automatische Uebernahme aus ALLRIS, SessionNet und anderen Systemen
- **Mandantenfaehig**: Eine Instanz fuer mehrere Kommunen (Schema-per-Tenant)

---

## Features

### Parlamentarisches Informationssystem
- Vollstaendige OParl-1.1-Implementierung (alle 12 Objekttypen)
- Gremien-, Sitzungs- und Vorlagenverwaltung
- Tagesordnungserstellung mit Drag-and-Drop
- Beschlussverfolgung und Statustracking
- Fraktions- und Mitgliederverwaltung

### Buergerportal
- Oeffentliche Sitzungskalender und Tagesordnungen
- Volltextsuche ueber alle parlamentarischen Dokumente
- Abonnements fuer Themen und Gremien (E-Mail/RSS)
- Barrierefreie Oberflaeche (WCAG 2.1 AA)
- Responsive Design fuer mobile Endgeraete

### Dokumentenmanagement
- Integrierte Dokumentenverwaltung mit MinIO (S3-kompatibel)
- Automatische Texterkennung (OCR) fuer gescannte Dokumente
- Versionierung und Archivierung
- Anbindung an externe DMS (d.velop, enaio, nscale)

### Migration
- Automatischer Import aus ALLRIS, SessionNet, MORE!Software
- OParl-Import von anderen OParl-kompatiblen Systemen
- CSV/Excel-Import fuer Altdaten
- Validierung und Zuordnung waehrend der Migration

### Suche
- Elasticsearch-basierte Volltextsuche
- Facettierte Suche nach Gremium, Zeitraum, Dokumenttyp
- Autovervollstaendigung und Suchvorschlaege
- Hervorhebung von Suchtreffern in Dokumenten

### Multi-Tenant
- Schema-per-Tenant-Architektur in PostgreSQL
- Tenant-spezifische Konfiguration und Branding
- Gemeinsame Infrastruktur, getrennte Daten
- Zentrales Management ueber Admin-Panel

---

## Schnellstart

### Voraussetzungen

- Docker >= 24.0 und Docker Compose >= 2.20
- Git
- 4 GB RAM (Entwicklung), 8 GB RAM (Produktion)

### Installation

```bash
# Repository klonen
git clone https://github.com/aitema-gmbh/ratsinformationssystem.git
cd ratsinformationssystem

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env nach Bedarf anpassen

# Development-Umgebung starten
make dev

# Datenbank-Migrationen ausfuehren
make db-migrate

# Demo-Daten laden (optional)
make db-seed
```

### Services (Development)

| Service         | URL                           | Beschreibung              |
|-----------------|-------------------------------|---------------------------|
| Backend API     | http://localhost:8000         | FastAPI Backend           |
| API Docs        | http://localhost:8000/docs    | Swagger UI                |
| OParl API       | http://localhost:8000/oparl/v1| OParl 1.1 Einstiegspunkt |
| Frontend        | http://localhost:3000         | Next.js Frontend          |
| Elasticsearch   | http://localhost:9200         | Suchindex                 |

---

## OParl 1.1 API

Alle 12 OParl-Objekttypen sind vollstaendig implementiert.

### Einstiegspunkt

```
GET /oparl/v1/system
```

### Endpoints

| Endpoint                              | OParl-Typ          | Beschreibung                    |
|---------------------------------------|--------------------|---------------------------------|
| `/oparl/v1/system`                    | `oparl:System`     | Systemweite Informationen       |
| `/oparl/v1/body`                      | `oparl:Body`       | Koerperschaften (Kommunen)      |
| `/oparl/v1/body/{id}/organization`    | `oparl:Organization`| Gremien und Fraktionen         |
| `/oparl/v1/body/{id}/person`          | `oparl:Person`     | Personen / Ratsmitglieder       |
| `/oparl/v1/body/{id}/meeting`         | `oparl:Meeting`    | Sitzungen                       |
| `/oparl/v1/body/{id}/paper`           | `oparl:Paper`      | Vorlagen und Antraege           |
| `/oparl/v1/body/{id}/legislation-term`| `oparl:LegislativeTerm`| Legislaturperioden         |
| `/oparl/v1/meeting/{id}/agenda-item`  | `oparl:AgendaItem` | Tagesordnungspunkte             |
| `/oparl/v1/paper/{id}/consultation`   | `oparl:Consultation`| Beratungen                    |
| `/oparl/v1/organization/{id}/membership`| `oparl:Membership`| Mitgliedschaften              |
| `/oparl/v1/file/{id}`                 | `oparl:File`       | Dateien und Dokumente           |
| `/oparl/v1/location/{id}`             | `oparl:Location`   | Ortsangaben                     |

### Verwaltungs-API

| Endpoint                    | Methode  | Beschreibung                      |
|-----------------------------|----------|-----------------------------------|
| `/api/v1/admin/tenants`     | GET/POST | Mandantenverwaltung               |
| `/api/v1/admin/users`       | GET/POST | Benutzerverwaltung                |
| `/api/v1/admin/import`      | POST     | Datenimport (ALLRIS/SessionNet)   |
| `/api/v1/workflow/meetings` | GET/POST | Sitzungsworkflow                  |
| `/api/v1/workflow/papers`   | GET/POST | Vorlagenworkflow                  |

---

## Architektur

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    Reverse Proxy                        │
                    │                  (Nginx / Caddy)                        │
                    └──────────┬──────────────────┬──────────────────┬────────┘
                               │                  │                  │
                    ┌──────────▼───────┐ ┌────────▼────────┐ ┌──────▼────────┐
                    │   Next.js 14     │ │   FastAPI        │ │   Keycloak    │
                    │   Frontend       │ │   Backend        │ │   Auth/SSO    │
                    │   (SSR + CSR)    │ │   (OParl + API)  │ │   (BundID)    │
                    │   Port 3000      │ │   Port 8000      │ │   Port 8080   │
                    └──────────────────┘ └────────┬─────────┘ └───────────────┘
                                                  │
                         ┌────────────────────────┼────────────────────────┐
                         │                        │                        │
              ┌──────────▼────────┐   ┌───────────▼──────────┐   ┌────────▼────────┐
              │   PostgreSQL 16   │   │   Elasticsearch 8    │   │   Redis 7       │
              │   (Schema/Tenant) │   │   (Volltextsuche)    │   │   (Cache/Queue) │
              │   Port 5432       │   │   Port 9200          │   │   Port 6379     │
              └───────────────────┘   └──────────────────────┘   └─────────────────┘
                                                                          │
                                                                 ┌────────▼────────┐
                                                                 │   MinIO (S3)    │
                                                                 │   (Dokumente)   │
                                                                 │   Port 9000     │
                                                                 └─────────────────┘
```

---

## Tech Stack

| Komponente      | Technologie                         | Version  |
|-----------------|-------------------------------------|----------|
| Backend         | Python / FastAPI / SQLAlchemy 2.0   | 3.12     |
| Frontend        | React / Next.js (App Router, SSR)   | 14       |
| Datenbank       | PostgreSQL                          | 16       |
| Suche           | Elasticsearch                       | 8.12     |
| Cache / Queue   | Redis                               | 7        |
| Dokumentenspeicher | MinIO (S3-kompatibel)            | latest   |
| Auth / SSO      | Keycloak (BundID-kompatibel)        | 23.0     |
| ORM             | SQLAlchemy 2.0 (async)              | 2.0      |
| Migrationen     | Alembic                             | latest   |
| Linting         | Ruff, Mypy, ESLint                  | latest   |
| Container       | Docker / Docker Compose             | 24+      |
| Reverse Proxy   | Nginx (Prod)                        | 1.25     |

---

## Projektstruktur

```
ratsinformationssystem/
├── backend/                  # Python FastAPI Backend
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── oparl/       # OParl 1.1 Endpunkte
│   │   │   ├── admin/       # Administrations-API
│   │   │   └── workflow/     # Workflow-Endpunkte
│   │   ├── core/             # Konfiguration, Security
│   │   ├── models/           # SQLAlchemy-Modelle
│   │   ├── schemas/          # Pydantic-Schemas
│   │   ├── services/         # Business-Logik
│   │   ├── scripts/          # CLI-Skripte
│   │   └── seeds/            # Demo-Daten
│   ├── tests/                # pytest Tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # Next.js 14 Frontend
│   ├── src/
│   │   ├── app/              # App Router Pages
│   │   └── components/       # React-Komponenten
│   ├── package.json
│   └── Dockerfile
├── migrations/               # Alembic-Migrationen
│   └── versions/
├── config/
│   ├── keycloak/             # Keycloak Realm-Export
│   ├── nginx/                # Nginx-Konfiguration
│   └── ssl/                  # SSL-Zertifikate
├── scripts/                  # Deployment- und Hilfs-Skripte
├── static/                   # Statische Assets
├── docs/                     # Dokumentation
├── tests/                    # Integrationstests
├── backups/                  # Datenbank-Backups
├── docker-compose.yml        # Development
├── docker-compose.prod.yml   # Produktion
├── Makefile                  # Build-Kommandos
├── alembic.ini               # Alembic-Konfiguration
├── .env.example              # Umgebungsvariablen-Vorlage
├── LICENSE                   # EUPL-1.2
└── README.md
```

---

## Migration von Bestandssystemen

aitema|Rats unterstuetzt die automatische Migration aus verbreiteten Ratsinformationssystemen:

| Quellsystem     | Format              | Status         |
|-----------------|---------------------|----------------|
| ALLRIS          | REST API / DB-Dump  | Unterstuetzt   |
| SessionNet      | SOAP / CSV-Export   | Unterstuetzt   |
| MORE!Software   | CSV-Export          | Unterstuetzt   |
| OParl-Systeme   | OParl 1.0 / 1.1    | Unterstuetzt   |
| Eigenentwicklung| CSV / Excel         | Unterstuetzt   |

```bash
# ALLRIS-Import starten
make db-migrate
python -m app.scripts.import_allris --source /path/to/export

# OParl-Import
python -m app.scripts.import_oparl --url https://oparl.example.de/api/v1/system
```

---

## Deployment

### Produktion mit Docker Compose

```bash
# Produktions-Stack starten
docker compose -f docker-compose.prod.yml up -d

# Logs anzeigen
docker compose -f docker-compose.prod.yml logs -f backend

# Backup erstellen
docker exec ris-postgres-prod pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup.sql
```

### Empfohlene Hardware (Produktion)

| Groesse          | vCPU | RAM   | Speicher | Kommunen |
|-----------------|------|-------|----------|----------|
| Small           | 4    | 8 GB  | 100 GB   | 1-5      |
| Medium          | 8    | 16 GB | 250 GB   | 5-20     |
| Large           | 16   | 32 GB | 500 GB   | 20+      |

---

## COSS-Modell (Commercial Open Source)

aitema|Rats folgt dem COSS-Modell und bietet verschiedene Nutzungsoptionen:

| Merkmal                       | Community (EUPL)     | Managed              | Enterprise           |
|-------------------------------|----------------------|----------------------|----------------------|
| Quellcode                     | Vollstaendig         | Vollstaendig         | Vollstaendig         |
| OParl 1.1 API                 | Ja                   | Ja                   | Ja                   |
| Buergerportal                 | Ja                   | Ja                   | Ja                   |
| Self-Hosting                  | Ja                   | Ja                   | Ja                   |
| Docker Images (GHCR)          | Ja                   | Ja                   | Ja                   |
| Managed Hosting               | --                   | Ja                   | Ja                   |
| SLA / Support                 | Community            | 48h Response         | 4h Response          |
| Migration aus ALLRIS u.a.     | Doku                 | Begleitet            | Vollservice          |
| DMS-Integration               | MinIO                | MinIO + d.velop      | Alle DMS             |
| BundID / SSO                  | Doku                 | Einrichtung          | Vollservice          |
| Schulung                      | --                   | Online               | Vor-Ort              |
| Anpassungen / Branding        | --                   | Auf Anfrage          | Inklusive            |

---

## Development

### Lokale Entwicklung

```bash
# Backend im Reload-Modus
make dev-backend

# Frontend separat starten
make dev-frontend

# Tests ausfuehren
make test

# OParl-Konformitaetstests
make test-oparl

# Linting
make lint
```

### Code Style

- **Python**: Ruff (Linting + Formatting), Mypy (Type Checking)
- **TypeScript/React**: ESLint, Prettier
- **Commits**: Conventional Commits (feat:, fix:, docs:, etc.)

---

## Contributing

Beitraege sind willkommen! Bitte lies unsere [CONTRIBUTING.md](CONTRIBUTING.md) fuer
Details zum Entwicklungsprozess, Code-Style und wie du Pull Requests einreichst.

---

## Lizenz

Copyright (c) 2025 aitema GmbH

Dieses Projekt ist unter der **European Union Public Licence (EUPL) v1.2** lizenziert.
Siehe [LICENSE](LICENSE) fuer den vollstaendigen Lizenztext.

Die EUPL ist kompatibel mit GPL-2.0, GPL-3.0, AGPL-3.0, LGPL, MPL, EPL, CeCILL
und weiteren Open-Source-Lizenzen. Siehe [EUPL-Kompatibilitaet](https://joinup.ec.europa.eu/collection/eupl/matrix-eupl-compatible-open-source-licences).

---

## Kontakt

**aitema GmbH**
- Web: [https://aitema.de](https://aitema.de)
- E-Mail: info@aitema.de
- GitHub: [https://github.com/aitema-gmbh](https://github.com/aitema-gmbh)

---

<div align="center">

Entwickelt mit Sorgfalt von [aitema GmbH](https://aitema.de) -- Digitale Loesungen fuer Kommunen.

</div>
