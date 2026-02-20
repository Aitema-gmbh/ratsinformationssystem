# Changelog

Alle wesentlichen Änderungen an aitema|Rats RIS werden in dieser Datei dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).
Versionierung nach [Semantic Versioning](https://semver.org/).

## [Unveröffentlicht]

## [1.0.0] – 2025-01-01

### Hinzugefügt
- OParl 1.1-konforme REST-API für maschinenlesbare Ratsdaten
- Volltext-Suche in allen Beschlüssen, Vorlagen und Protokollen
- Gremien- und Ausschussverwaltung
- Sitzungsmanagement mit Tagesordnungen und Beschlussverfolgung
- Mitglieder- und Fraktionsverwaltung
- Öffentliches Transparenzportal für Bürgerinnen und Bürger
- Kalender-Integration für Sitzungstermine (iCal-Export)
- Dokumenten-Viewer mit PDF-Vorschau im Browser
- Rollenbasiertes Zugriffsmanagement (öffentlich / Ratsmitglied / Verwaltung)
- Modernes UI mit aitema Design-System (Next.js, Inter-Font, Navy/Blue/Accent-Palette)
- Skeleton-Loader und optimistische UI-Updates
- Dark-Mode-Unterstützung
- Docker-Compose-Deployment inkl. PostgreSQL-Migration
- Datenbankschema-Dokumentation (OParl 1.1 + Alembic)
- System-Architektur-Dokumentation
- OpenAPI 3.1 Spezifikation
- publiccode.yml für opencode.de-Kompatibilität
- End-to-End-Tests mit Playwright und axe-core Barrierefreiheits-Audit
- Issue-Templates für Kommunen, Fehlerberichte und Förderanfragen
- Renovate-Bot für automatische Dependency-Updates
- CONTRIBUTING.md mit Entwickler-Richtlinien
- GitHub Actions CI/CD-Pipeline

### Technischer Stack
- **Frontend/Backend:** Next.js 14, React, TypeScript
- **Datenbank:** PostgreSQL via Supabase
- **Styling:** Tailwind CSS 3.4
- **Lizenz:** AGPL-3.0

[Unveröffentlicht]: https://github.com/Aitema-gmbh/ratsinformationssystem/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Aitema-gmbh/ratsinformationssystem/releases/tag/v1.0.0
