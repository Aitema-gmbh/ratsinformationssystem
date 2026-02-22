<div align="center">

# aitema|RIS

**Offenes Ratsinformationssystem — OParl 1.1, BITV 2.0 AA, MIT-lizenziert**

[![MIT License](https://img.shields.io/badge/Lizenz-MIT-22c55e?style=flat-square)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-ris.aitema.de-3b82f6?style=flat-square)](https://ris.aitema.de)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat-square&logo=next.js)](https://nextjs.org)
[![OParl](https://img.shields.io/badge/OParl-1.1-f97316?style=flat-square)](https://oparl.org)
[![BITV](https://img.shields.io/badge/BITV-2.0%20AA-16a34a?style=flat-square)](https://www.gesetze-im-internet.de/bitv_2_0/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ed?style=flat-square&logo=docker)](docker-compose.quickstart.yml)

[**→ Live Demo**](https://ris.aitema.de) · [**Dokumentation**](docs/) · [**Bug melden**](https://github.com/Aitema-gmbh/ratsinformationssystem/issues) · [**Diskussion**](https://github.com/Aitema-gmbh/ratsinformationssystem/discussions)

</div>

---

## Was ist aitema|RIS?

aitema|RIS ist ein **offenes Ratsinformationssystem** für kommunale Gremienarbeit. Sitzungen, Tagesordnungen, Beschlussvorlagen und Mandatsträger werden transparent zugänglich — für Bürgerinnen, Bürger und die Verwaltung selbst.

Das System ist vollständig **OParl 1.1 kompatibel**, **BITV 2.0 AA konform** und läuft **selbst-gehostet** auf eurer eigenen Infrastruktur.

> **Warum Open Source?** Kommunale Demokratie braucht offene Werkzeuge. Wer Transparenz fordert, muss auch den eigenen Code offenlegen.

---

## Features

### 🏛️ Bürger-Transparenz-Portal

| Feature | Details |
|---------|---------|
| **Volltextsuche** | Alle Sitzungen, Vorlagen und Personen durchsuchbar |
| **Sitzungskalender** | Übersicht aller Gremiensitzungen mit Agenda-Vorschau |
| **Beschlussvorlagen** | Vollständige Dokumentenansicht mit Typ-Kategorisierung |
| **Personen & Gremien** | Mandatsträger-Profile mit Ausschuss-Zuordnung |
| **OParl 1.1 API** | Offene Datenschnittstelle für Drittanwendungen |

### ⚙️ Für Verwaltung & IT

| Feature | Details |
|---------|---------|
| **Barrierefreiheit** | BITV 2.0 AA konform (BFSG-Pflicht ab 28.06.2025) |
| **DSGVO-konform** | Keine externen Tracker, kein Google Fonts, selbst-gehostet |
| **Docker-native** | Ein Befehl, läuft überall |
| **OParl-Export** | Alle Daten maschinenlesbar abrufbar |
| **Traefik-ready** | Automatisches SSL via Let's Encrypt |

---

## Compliance

| Standard | Status |
|----------|--------|
| OParl 1.1 | ✅ vollständig implementiert |
| BITV 2.0 AA (Barrierefreiheit) | ✅ konform |
| BFSG (Barrierefreiheitsstärkungsgesetz) | ✅ ab 28.06.2025 |
| DSGVO | ✅ konform (keine Drittanbieter) |
| OZG 2.0 | ✅ kompatibel |

---

## Tech-Stack

```
Frontend:   Next.js 15 + React 19 + Tailwind CSS 3.4
            React Aria (Barrierefreiheits-Komponenten)
Backend:    Node.js API
Datenbank:  PostgreSQL + Redis
Deploy:     Docker Compose + Traefik + Let's Encrypt
```

---

## Schnellstart (5 Minuten)

```bash
git clone https://github.com/Aitema-gmbh/ratsinformationssystem.git
cd ratsinformationssystem

# Konfiguration
cp .env.example .env
# .env anpassen (Datenbankpasswort, Domain etc.)

# Starten
docker compose -f docker-compose.quickstart.yml up -d
```

Die App ist dann unter `http://localhost:3000` erreichbar.

**Für Produktion mit eigenem Domain:**

```bash
docker compose -f docker-compose.traefik.yml up -d
```

→ Vollständige Anleitung: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## Architektur

```
ris.aitema.de
├── /              →  Redirect auf /suche
├── /suche         →  Volltextsuche (Haupteinstieg)
├── /sitzungen     →  Sitzungskalender + Detailansicht
├── /vorlagen      →  Beschlussvorlagen mit Typ-Badges
├── /personen      →  Mandatsträger-Übersicht
└── /gremien       →  Ausschüsse & Gremien

OParl 1.1 API
├── GET /api/v1/oparl/system
├── GET /api/v1/oparl/bodies
├── GET /api/v1/oparl/meetings
├── GET /api/v1/oparl/papers
├── GET /api/v1/oparl/persons
└── GET /api/v1/oparl/organizations
```

**Informationsfluss:**

```
Ratssitzung  →  Digitale Vorlage  →  Volltextsuche  →  Öffentlich
   (intern)        (Verwaltung)       (aitema|RIS)     (Bürger)
```

---

## OParl 1.1

aitema|RIS implementiert [OParl 1.1](https://oparl.org) vollständig — den deutschen Standard für offene Ratsinformationssysteme. Das bedeutet:

- Alle Daten sind über eine standardisierte REST-API abrufbar
- Drittanwendungen (Apps, Visualisierungen, KI-Tools) können direkt auf die Daten zugreifen
- Kompatibel mit anderen OParl-fähigen Systemen (allris, Session, SD.NET, ...)

---

## Roadmap

- [x] Volltextsuche über alle Dokumente
- [x] OParl 1.1 API
- [x] BITV 2.0 AA Barrierefreiheit
- [x] Sitzungen, Vorlagen, Personen, Gremien
- [ ] Abstimmungsergebnisse (Ja/Nein/Enthaltung)
- [ ] iCal-Feed (Sitzungskalender abonnieren)
- [ ] LDAP/SAML Import (Ratsmitglieder aus bestehendem Verzeichnis)
- [ ] Einfache Sprache Toggle (A2-Level, BFSG)
- [ ] Multi-Mandanten (eine Instanz, mehrere Kommunen)

Ideen und Feature-Requests → [GitHub Discussions](https://github.com/Aitema-gmbh/ratsinformationssystem/discussions)

---

## Beitragen

Beiträge sind willkommen — von Bugfixes bis zu neuen Features.

```bash
# 1. Fork + Clone
git clone https://github.com/DEIN-USERNAME/ratsinformationssystem.git

# 2. Feature-Branch
git checkout -b feat/mein-feature

# 3. Entwickeln, testen, committen (Conventional Commits)
git commit -m "feat: kurze Beschreibung"

# 4. Pull Request öffnen
```

→ Vollständige Anleitung: [CONTRIBUTING.md](CONTRIBUTING.md)  
→ Verhaltenskodex: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)  
→ Sicherheitslücken melden: [SECURITY.md](SECURITY.md)

**Gute Einstiegspunkte:** [`good first issue`](https://github.com/Aitema-gmbh/ratsinformationssystem/issues?q=label%3A%22good+first+issue%22)

---

## Verwandte Projekte

| Projekt | Beschreibung |
|---------|-------------|
| [aitema\|Hinweis](https://github.com/Aitema-gmbh/hinweisgebersystem) | Anonymes Hinweisgebersystem (HinSchG) |
| [aitema\|Termin](https://github.com/Aitema-gmbh/terminvergabe) | Online-Terminvergabe für Behörden |

---

## Lizenz

MIT — frei nutzbar, auch für Kommunen und öffentliche Stellen.

```
Copyright (c) 2025 aitema GmbH
```

Vollständiger Lizenztext: [LICENSE](LICENSE)

---

<div align="center">

Entwickelt von [aitema GmbH](https://aitema.de) · AI Innovation for Public Sector  
[aitema.de](https://aitema.de) · [kontakt@aitema.de](mailto:kontakt@aitema.de)

*GovTech aus Deutschland — für Deutschland.*

</div>
