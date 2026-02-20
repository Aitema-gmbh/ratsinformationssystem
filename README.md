# aitema|Rats RIS – Open-Source-Ratsinformationssystem

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![GitHub Stars](https://img.shields.io/github/stars/Aitema-gmbh/ratsinformationssystem?style=social)](https://github.com/Aitema-gmbh/ratsinformationssystem/stargazers)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://github.com/Aitema-gmbh/ratsinformationssystem/pkgs/container/ratsinformationssystem)
[![OParl 1.1](https://img.shields.io/badge/OParl-1.1-brightgreen)](https://oparl.org)
[![opencode.de](https://img.shields.io/badge/opencode.de-Kompatibel-0069B4)](https://opencode.de)
[![API Docs](https://img.shields.io/badge/API-Dokumentation-orange)](https://aitema.de/api-docs/ratsinformationssystem)

Modernes, quelloffenes Ratsinformationssystem für Kommunen – OParl-konform, Next.js-Frontend, keine Lizenzkosten.

## 🏛️ Was ist ein Ratsinformationssystem?

Ratsinformationssysteme (RIS) ermöglichen Bürgerinnen und Bürgern, Ratsmitgliedern und der Verwaltung Zugang zu Sitzungen, Tagesordnungen, Vorlagen und Protokollen des Gemeinderats. aitema|Rats RIS implementiert den offenen [OParl-Standard](https://oparl.org/) für maximale Interoperabilität.

## 🆚 Warum kein ALLRIS oder Session?

| Feature | aitema\|Rats RIS | ALLRIS (CC e-gov) | Session (Somacos) |
|---------|----------------|-------------------|-------------------|
| Preis | **Kostenlos** | Lizenzpflichtig | Lizenzpflichtig |
| Technologie | Next.js 14 (2024) | Legacy .NET | Legacy Java |
| OParl-nativ | ✅ | ⚠️ Nachgerüstet | ⚠️ Nachgerüstet |
| Selbst-hostbar | ✅ | ⚠️ | ⚠️ |
| Open Source | ✅ | ❌ | ❌ |
| Responsive/Mobil | ✅ | ⚠️ | ⚠️ |

## 🚀 Schnellstart (Docker)

```bash
git clone https://github.com/Aitema-gmbh/ratsinformationssystem.git
cd ratsinformationssystem
cp .env.example .env
docker compose up -d
```

Öffne http://localhost:3000 – das RIS ist einsatzbereit!

## ✨ Funktionen

- **Volltextsuche** – Über alle Sitzungen, Vorlagen und Protokolle
- **Sitzungsübersicht** – Tagesordnungen, Beschlüsse, Dokumente
- **Vorlagen-Archiv** – Mit Typ-Badges und Status-Anzeige
- **Personen & Gremien** – Ratsmitglieder, Ausschüsse, Fraktionen
- **OParl-API** – Vollständige Implementierung des offenen Standards
- **Responsive Design** – Optimal auf Smartphone und Desktop
- **Skeleton-Loader** – Professionelles Ladeerlebnis
- **Barrierefreiheit** – WCAG 2.1 AA angestrebt

## 🏗️ Technologie

| Schicht | Technologie |
|---------|-------------|
| Frontend | Next.js 14 (App Router) |
| Styling | Tailwind CSS 3.4 |
| Sprache | TypeScript |
| API-Standard | OParl 1.1 |
| Datenbank | PostgreSQL 15 |
| Deployment | Docker Compose |
| Lizenz | AGPL-3.0 |

## 📞 Kontakt & Support

- **Bug melden:** [GitHub Issues](https://github.com/Aitema-gmbh/ratsinformationssystem/issues)
- **Kontakt:** kontakt@aitema.de

---
*Entwickelt mit ❤️ in Deutschland | [aitema.de](https://aitema.de)*
