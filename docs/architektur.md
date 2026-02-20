# aitema|Ratsinfo – Architektur-Übersicht

## System-Übersicht

```
┌─────────────────────────────────────────────────────────┐
│                 aitema|Ratsinfo                          │
│                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  Next.js 14 │───▶│  Supabase   │───▶│ PostgreSQL  │  │
│  │  Frontend   │    │   Backend   │    │  (managed)  │  │
│  │  (SSR/SSG)  │    │  (REST+RLS) │    │             │  │
│  └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                  │                             │
│         └──────────────────┘                             │
│              Vercel / Cloudflare Pages                   │
│              (CDN + Edge Deployment)                     │
└─────────────────────────────────────────────────────────┘
```

## Komponenten

### Frontend (Next.js 14)
- **Framework:** Next.js 14 mit App Router und TypeScript
- **Rendering:** SSR (Server-Side Rendering) für SEO-Optimierung, SSG für statische Seiten
- **UI-Library:** Tailwind CSS + aitema Design-System
- **OParl-Schnittstelle:** Vollständige OParl 1.1 API-Kompatibilität

### Backend (Supabase)
- **Plattform:** Supabase (Open Source Firebase-Alternative)
- **API:** Auto-generierte REST API via PostgREST
- **Echtzeit:** Supabase Realtime für Live-Updates im Ratsinformationssystem
- **Auth:** Supabase Auth mit Row-Level Security (RLS)
- **Storage:** Supabase Storage für Sitzungsprotokolle und Dokumente

### Datenbank (PostgreSQL via Supabase)
- **Version:** PostgreSQL 15+
- **Sicherheit:** Row-Level Security (RLS) für granulare Zugriffssteuerung
- **Volltextsuche:** PostgreSQL Full-Text Search für Dokumente und Beschlüsse
- **Backup:** Tägliche automatische Backups via Supabase

## Deployment

```bash
# Umgebungsvariablen
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJxxx...
SUPABASE_SERVICE_ROLE_KEY=eyJxxx...

# Build und Deployment
npm install
npm run build
# Automatisches Deployment via GitHub Actions → Vercel/Cloudflare Pages
```

## OParl-Schnittstelle

Das System implementiert den offenen Standard OParl 1.1 für kommunale Ratsinformationssysteme:

- **`/oparl/v1.1/system`** – System-Endpunkt
- **`/oparl/v1.1/body`** – Körperschaften (Kommunen)
- **`/oparl/v1.1/meeting`** – Sitzungen
- **`/oparl/v1.1/paper`** – Drucksachen
- **`/oparl/v1.1/person`** – Personen (Ratsmitglieder)

## Datenschutz-Architektur

1. **Öffentliche Transparenz:** Ratsinformationen sind standardmäßig öffentlich
2. **Zugangskontrolle:** Interne Dokumente nur für authentifizierte Nutzer (RLS)
3. **Verschlüsselung:** TLS 1.3 in Transit, PostgreSQL-Verschlüsselung at Rest
4. **DSGVO-konform:** Personenbezogene Daten (Ratsmitglieder) nach DSGVO verarbeitet
5. **Self-hosted:** Supabase kann vollständig selbst gehostet werden

## Lizenz

AGPL-3.0-or-later – Open Source, OParl-zertifiziert kompatibel
