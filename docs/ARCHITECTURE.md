# aitema|RIS – Architektur

## System-Übersicht

```
┌────────────────────────────────────────────────────┐
│                  ris.aitema.de                      │
│               Traefik Reverse Proxy                 │
└─────────┬──────────────────┬────────────────────────┘
          │                  │
   ┌──────▼──────┐    ┌──────▼──────┐
   │  Next.js 14 │    │   FastAPI   │
   │  Frontend   │    │   Backend   │
   │  :3000      │    │   :8000     │
   └──────┬──────┘    └──────┬──────┘
          │                  │
   ┌──────▼──────────────────▼──────────────┐
   │  PostgreSQL 16 + pgvector               │
   │  Elasticsearch 8.11                     │
   └─────────────────────────────────────────┘
```

## Komponenten

| Komponente | Technologie | Port | Beschreibung |
|------------|------------|------|--------------|
| Frontend | Next.js 14 | :3000 | Bürger-Portal, Admin |
| Backend API | FastAPI (Python) | :8000 | REST API, OParl |
| Datenbank | PostgreSQL 16 + pgvector | :5432 | Daten + Embeddings |
| Suche | Elasticsearch 8.11 | :9200 | Volltext-Index |
| Auth | Keycloak | :8080 | OIDC/PKCE SSO |
| Analytics | Plausible | :8888 | Cookiefrei, DSGVO |

## Datenfluss: Volltextsuche

```
Nutzer gibt Suchbegriff ein
→ GET /api/v1/search?q=...
  ├── Elasticsearch: BM25 Fulltext-Ranking
  ├── pgvector: Cosine-Similarity (Semantik)
  └── Hybrid-Ranking: 0.6 × BM25 + 0.4 × Semantic
→ Ergebnisse: Sitzungen, Vorlagen, Personen, Gremien
→ KI-Snippet: Claude Haiku fasst Top-Treffer zusammen
```

## Datenfluss: Semantische Suche

```
Neue Vorlage wird angelegt
→ POST /api/v1/papers
  ├── PostgreSQL: Vorlage gespeichert
  └── Async Worker: Anthropic voyage-3 Embedding
        → pgvector-Spalte: embedding VECTOR(1536)
        → IVFFlat Index aktualisiert

Suchanfrage
→ voyage-3 Embedding der Anfrage
→ SELECT ... ORDER BY embedding <=> query_embedding
→ Hybrid-Ranking mit Elasticsearch BM25
```

## Multi-Tenant-Architektur

```
PostgreSQL
├── Schema: tenant_muenchen   (München)
├── Schema: tenant_augsburg   (Augsburg)
├── Schema: tenant_nuernberg  (Nürnberg)
└── Schema: public            (Shared: Auth, Config)

Elasticsearch
├── Index: muenchen_papers
├── Index: augsburg_papers
└── Index: nuernberg_papers
```

- Alembic-Migrationen laufen für alle Tenant-Schemas
- Keycloak: eigene Realm pro Mandant oder Gruppen-basiert
- Next.js: Subdomain-Routing (muenchen.ris.aitema.de)

## KI-Funktionen

### Zusammenfassungen (Claude Haiku)
```
Input:  Volltext der Beschlussvorlage (max 8000 Token)
Prompt: "Fasse diese Vorlage in 3 Sätzen zusammen..."
Output: Zusammenfassung, gespeichert in papers.summary
Label:  "KI-generiert" (EU AI Act Transparenz)
```

### Einfache Sprache (Claude Haiku)
```
Input:  Beschlussvorlage oder Zusammenfassung
Prompt: "Schreibe diesen Text in Einfacher Sprache (A2)..."
Output: Vereinfachter Text, on-demand generiert
Cache:  Redis (1h TTL)
```

## OParl 1.1 Implementierung

Alle OParl-Objekte werden aus dem PostgreSQL-Schema gemappt:

| OParl-Objekt | PostgreSQL-Tabelle | FastAPI-Endpoint |
|-------------|-------------------|-----------------|
| System | config | /api/v1/oparl/system |
| Body | tenants | /api/v1/oparl/bodies |
| Meeting | sessions | /api/v1/oparl/meetings |
| AgendaItem | agenda_items | /api/v1/oparl/agenda-items |
| Paper | papers | /api/v1/oparl/papers |
| Person | persons | /api/v1/oparl/persons |
| Organization | committees | /api/v1/oparl/organizations |

## Datenbankschema (Kernentitäten)

```
Tenant (Mandant/Kommune)
  └── Session[] (Ratssitzungen)
        ├── AgendaItem[] (Tagesordnungspunkte)
        │     └── Paper[] (Beschlussvorlagen)
        │           ├── summary: TEXT (KI-generiert)
        │           └── embedding: VECTOR(1536)
        ├── VotingResult[] (Abstimmungsergebnisse)
        └── Person[] via Committee[]

Person (Ratsmitglied)
  ├── Committee[] (Gremienmitgliedschaften)
  └── Vote[] (namentliche Abstimmungen)
```

## Deployment (Hetzner)

```
/opt/aitema/ratsinformationssystem/
├── docker-compose.yml
├── docker-compose.prod.yml
├── docker-compose.traefik.yml
├── alembic.ini
├── migrations/
└── .env.production
```

## Sicherheit

- **HTTPS**: Traefik + Let's Encrypt
- **Auth**: Keycloak OIDC/PKCE, Rollen: Admin, Redakteur, Leser
- **OParl**: Öffentliche Endpunkte ohne Auth (nur GET)
- **Admin**: Keycloak-geschützt (Admin-Rolle erforderlich)
- **Rate Limiting**: FastAPI Slowapi (200 req/min)
- **CORS**: Nur ris.aitema.de und Subdomains
