# Beitragen zu aitema|Rats

Vielen Dank fuer dein Interesse an aitema|Rats\! Wir freuen uns ueber Beitraege
aus der Community. Dieses Dokument erklaert, wie du zum Projekt beitragen kannst.

## Verhaltenskodex

Wir erwarten von allen Beteiligten einen respektvollen und konstruktiven Umgang.
Diskriminierung, Beleidigung oder anderes schaedliches Verhalten wird nicht toleriert.

## Wie kann ich beitragen?

### Fehler melden

1. Pruefe, ob der Fehler bereits als [Issue](https://github.com/aitema-gmbh/ratsinformationssystem/issues) gemeldet wurde
2. Erstelle ein neues Issue mit:
   - Klare Beschreibung des Problems
   - Schritte zur Reproduktion
   - Erwartetes vs. tatsaechliches Verhalten
   - Screenshots (falls relevant)
   - Umgebung (Browser, OS, Docker-Version)

### Feature vorschlagen

1. Oeffne ein Issue mit dem Label `enhancement`
2. Beschreibe das gewuenschte Feature und den Anwendungsfall
3. Bei OParl-relevanten Features: Referenz auf die OParl-Spezifikation angeben

### Code beitragen

#### Voraussetzungen

- Python 3.12+
- Node.js 20+
- Docker und Docker Compose
- Git

#### Fork und Branch Workflow

```bash
# 1. Repository forken (ueber GitHub UI)

# 2. Fork klonen
git clone https://github.com/DEIN-USER/ratsinformationssystem.git
cd ratsinformationssystem

# 3. Upstream hinzufuegen
git remote add upstream https://github.com/aitema-gmbh/ratsinformationssystem.git

# 4. Feature-Branch erstellen
git checkout -b feat/mein-feature

# 5. Aenderungen vornehmen und committen
git add .
git commit -m "feat: Beschreibung der Aenderung"

# 6. Branch pushen
git push origin feat/mein-feature

# 7. Pull Request ueber GitHub UI erstellen
```

#### Commit-Konventionen

Wir verwenden [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix    | Verwendung                              |
|-----------|-----------------------------------------|
| `feat:`   | Neues Feature                           |
| `fix:`    | Bugfix                                  |
| `docs:`   | Dokumentation                           |
| `style:`  | Formatierung (kein Code-Aenderung)      |
| `refactor:` | Refactoring                           |
| `test:`   | Tests hinzufuegen/aendern               |
| `chore:`  | Build, CI, Abhaengigkeiten              |

#### Code Style

**Python (Backend)**:
- Formatter: **Ruff** (`ruff format`)
- Linter: **Ruff** (`ruff check`)
- Type-Checking: **Mypy** (`mypy app/`)
- Zeilenlaenge: 120 Zeichen
- Docstrings: Google-Style

```bash
# Vor dem Commit ausfuehren
cd backend
ruff format app/ tests/
ruff check app/ tests/ --fix
mypy app/ --ignore-missing-imports
```

**TypeScript/React (Frontend)**:
- Formatter: **Prettier**
- Linter: **ESLint**
- Strikte TypeScript-Konfiguration

```bash
# Vor dem Commit ausfuehren
cd frontend
npm run lint -- --fix
npm run type-check
```

#### Tests schreiben

- Jede neue Funktion muss mit Tests abgedeckt sein
- Backend: **pytest** mit async-Support
- Frontend: **Jest** / **React Testing Library**
- OParl-Endpunkte: Zusaetzlich gegen OParl-Validator testen

```bash
# Backend-Tests
cd backend
python -m pytest tests/ -v

# OParl-Konformitaetstests
python -m pytest tests/test_oparl.py -v

# Frontend-Tests
cd frontend
npm test
```

#### OParl-Konformitaet

Bei Aenderungen an OParl-Endpunkten:
- Spezifikation beachten: https://oparl.org/spezifikation/
- Alle 12 Objekttypen muessen konform bleiben
- Pagination (cursor-based) muss funktionieren
- JSON-LD-Kontext muss korrekt sein

### Pull Request erstellen

1. PR-Titel folgt Conventional Commits
2. Beschreibung enthaelt:
   - Was wurde geaendert?
   - Warum wurde es geaendert?
   - Wie kann es getestet werden?
3. CI muss gruen sein (Linting, Tests, Build)
4. Mindestens ein Review erforderlich

## Fragen?

- GitHub Discussions: [Diskussionen](https://github.com/aitema-gmbh/ratsinformationssystem/discussions)
- E-Mail: dev@aitema.de

Vielen Dank fuer deinen Beitrag\!
