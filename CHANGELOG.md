# Änderungsprotokoll

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt hält sich an [Semantische Versionierung](https://semver.org/spec/v2.0.0.html).

## [Unveröffentlicht]

### Hinzugefügt
- Modernes UI-Design mit aitema Design-System (Inter, Navy/Blue/Accent-Palette)
- Öffentliches Ratsportal mit filterbarer Tagesordnungs-Ansicht
- Volltext-Suche über alle Drucksachen und Protokolle
- Kalender-Integration für Sitzungstermine (iCal-Export)
- Dokumenten-Viewer mit PDF-Vorschau im Browser
- Rollen-basiertes Zugriffsmanagement (öffentlich / Ratsmitglied / Verwaltung)
- API-Endpunkte für OParl-Standard (offene Ratsinformations-Schnittstelle)
- publiccode.yml für opencode.de-Kompatibilität
- Issue-Templates für Kommunen, Fehlerberichte und Förderanfragen
- GitHub Actions: Semantic Release, Renovate Bot, Willkommens-Bot
- End-to-End-Tests mit Playwright
- Docker-Compose-Deployment inkl. PostgreSQL-Migration

### Geändert
- Dashboard-Layout auf moderne Card-Ansicht umgestellt
- Suchfunktion auf Elasticsearch-Backend migriert

## [1.0.0] – 2024-01-01

### Hinzugefügt
- Erstveröffentlichung
- Verwaltung von Ratssitzungen, Tagesordnungen und Beschlüssen
- Drucksachen-Archiv mit Versionierung
- Öffentliche Sitzungskalender-Ansicht
- Bürgerportal für Einsichtnahme ohne Registrierung
- OParl-1.1-konforme REST-API
- DSGVO-konformes Benutzer- und Rollenmanagement
- Docker-Compose-Deployment
- Mehrsprachige Benutzeroberfläche (Deutsch)
