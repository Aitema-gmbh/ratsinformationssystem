# aitema|Rats RIS – Open-Source-Ratsinformationssystem

![GitHub License](https://img.shields.io/github/license/Aitema-gmbh/ratsinformationssystem?style=flat-square&color=blue)
![GitHub Stars](https://img.shields.io/github/stars/Aitema-gmbh/ratsinformationssystem?style=flat-square)
![publiccode.yml](https://img.shields.io/badge/publiccode-0.4-brightgreen?style=flat-square)
![OParl](https://img.shields.io/badge/OParl-1.1-orange?style=flat-square)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square&logo=next.js)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker&logoColor=white)


[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![OParl konform](https://img.shields.io/badge/OParl-konform-green)](https://oparl.org)
[![Made in Germany](https://img.shields.io/badge/Made_in-Germany-black)](https://aitema.de)

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
