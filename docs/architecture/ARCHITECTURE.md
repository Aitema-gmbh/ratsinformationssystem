# aitema|Rats – Technische Architektur

## Übersicht

aitema|Rats ist ein Next.js-basiertes Ratsinformationssystem mit OParl 1.1 API-Konformität für kommunale Gremienarbeit.

## System-Architektur

```mermaid
graph TB
    subgraph Öffentlicher Zugang
        CIT[Bürger/Browser]
        INT[Intranet / Verwaltung]
    end
    
    subgraph Reverse Proxy
        T[Traefik<br/>SSL/TLS]
    end
    
    subgraph Next.js App
        SSR[Server-Side Rendering<br/>React Pages]
        API_ROUTES[API Routes<br/>/api/*]
        OPARL[OParl 1.1 Handler<br/>/api/oparl/v1.1/*]
        SEARCH[Volltextsuche<br/>PostgreSQL FTS]
    end
    
    subgraph Backend
        SUPA[Supabase<br/>PostgreSQL + Auth]
        STORAGE[MinIO / Supabase Storage<br/>Dokumenten-Ablage]
    end
    
    CIT --> T --> SSR
    CIT --> T --> OPARL
    INT --> T --> API_ROUTES
    SSR --> SUPA
    API_ROUTES --> SUPA
    OPARL --> SUPA
    SEARCH --> SUPA
    API_ROUTES --> STORAGE
```

## OParl 1.1 Konformität

```mermaid
graph LR
    CLIENT[OParl-Client<br/>z.B. Lokalpolitik-App]
    SYSTEM[GET /api/oparl/v1.1/system]
    BODY[GET /api/oparl/v1.1/body/1]
    MEETING[GET /api/oparl/v1.1/meeting]
    PAPER[GET /api/oparl/v1.1/paper]
    PERSON[GET /api/oparl/v1.1/person]
    ORG[GET /api/oparl/v1.1/organization]
    
    CLIENT --> SYSTEM
    SYSTEM --> BODY
    BODY --> MEETING
    BODY --> PAPER
    BODY --> PERSON
    BODY --> ORG
```

## Datenfluss: Sitzungsmanagement

```mermaid
sequenceDiagram
    participant ADMIN as Verwaltung
    participant APP as Next.js App
    participant DB as Supabase/PostgreSQL
    participant STORE as Dokumenten-Storage
    
    ADMIN->>APP: Neue Sitzung anlegen
    APP->>DB: INSERT oparl_meeting
    ADMIN->>APP: Dokument hochladen (PDF)
    APP->>STORE: Datei speichern
    STORE->>APP: Storage-URL zurück
    APP->>DB: INSERT oparl_file (mit URL)
    Note over DB: Automatische<br/>OParl-Serialisierung
    APP->>ADMIN: Sitzung veröffentlicht
```

## Komponenten

### Next.js App (Frontend + API)
- **Framework**: Next.js 14 mit App Router
- **Rendering**: SSR + SSG für öffentliche Seiten
- **Styling**: Tailwind CSS 3.4
- **Suche**: PostgreSQL Full-Text Search (tsvector)
- **Authentifizierung**: Supabase Auth (JWT)

### OParl-Schnittstelle
- **Standard**: OParl 1.1 vollständig implementiert
- **Endpunkte**: System, Body, Organization, Person, Meeting, AgendaItem, Paper, File
- **Format**: JSON-LD
- **Paginierung**: Automatisch via cursor-based pagination

### Datenbank (Supabase)
- **PostgreSQL 15**: Hauptdatenbank auf Supabase
- **Row Level Security**: Feingranulare Zugriffssteuerung
- **Realtime**: Supabase Realtime für Live-Updates
- **Storage**: Supabase Storage für Dokumente

## Deployment

```mermaid
graph LR
    GH[GitHub<br/>Aitema-gmbh/ratsinformationssystem]
    GHCR[GitHub Container Registry<br/>ghcr.io/aitema-gmbh]
    SERVER[Hetzner Server<br/>Docker Compose]
    
    GH -->|git push main| GH
    GH -->|GitHub Actions<br/>Build + Push| GHCR
    GHCR -->|Pull & Deploy| SERVER
```

## Technologie-Stack

| Layer | Technologie | Version |
|-------|-------------|---------|
| Framework | Next.js | 14.x |
| Sprache | TypeScript | 5.x |
| Styling | Tailwind CSS | 3.4.x |
| Datenbank | Supabase (PostgreSQL) | 15.x |
| ORM | Prisma | 5.x |
| Suche | PostgreSQL FTS | nativ |
| Container | Docker | 24.x |
| Standard | OParl | 1.1 |
