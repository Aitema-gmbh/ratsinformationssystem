# aitema|Rats RIS – Datenbankschema

## Übersicht

Das System nutzt **PostgreSQL via Alembic-Migrationen** als Datenbankbackend.
Das Schema implementiert den **OParl 1.1 Standard** vollständig plus aitema-spezifische Erweiterungen.

- **Migration-Tool:** Alembic (Python)
- **Datenbank:** PostgreSQL 15
- **Aktuelle Migration:** `001_initial_oparl_schema`
- **Multi-Tenant:** Ja, über `tenant`-Tabelle mit eigenem Schema pro Mandant

---

## Kernentitäten (OParl 1.1)

### Gemeinsame Basisfelder (alle OParl-Objekte)

Alle OParl-Tabellen enthalten folgende Standardfelder:

```sql
id          UUID PRIMARY KEY
oparl_type  TEXT NOT NULL          -- z.B. "https://schema.oparl.org/1.1/Body"
created     TIMESTAMPTZ DEFAULT NOW()
modified    TIMESTAMPTZ DEFAULT NOW()
deleted     BOOLEAN DEFAULT false
keyword     TEXT[]                  -- Array von Schlagwörtern
web         TEXT                    -- öffentliche URL
license     TEXT                    -- Lizenz-URL
```

---

### Mandanten (`tenant`)

Multi-Tenant-Verwaltung für verschiedene Kommunen.

```sql
CREATE TABLE tenant (
  id              UUID PRIMARY KEY,
  slug            VARCHAR(100) UNIQUE NOT NULL,  -- URL-Slug, z.B. "berlin-mitte"
  name            VARCHAR(512) NOT NULL,
  ags             VARCHAR(12) UNIQUE,             -- Amtlicher Gemeindeschlüssel
  domain          VARCHAR(255) UNIQUE,            -- Custom Domain
  config          JSONB DEFAULT \{}\,
  keycloak_realm  VARCHAR(255),                   -- SSO-Integration
  is_active       BOOLEAN DEFAULT true,
  is_trial        BOOLEAN DEFAULT false,
  contact_email   VARCHAR(255),
  contact_name    VARCHAR(255),
  contact_phone   VARCHAR(100),
  notes           TEXT,
  schema_created  BOOLEAN DEFAULT false,          -- DB-Schema angelegt?
  created         TIMESTAMPTZ DEFAULT NOW(),
  modified        TIMESTAMPTZ DEFAULT NOW()
);
```

---

### Standort (`location`)

Geographische Ortsangaben für Sitzungen, Dokumente und Personen.

```sql
CREATE TABLE location (
  id              UUID PRIMARY KEY,
  -- OParl-Basisfelder --
  street_address  VARCHAR(512),
  room            VARCHAR(255),
  postal_code     VARCHAR(20),
  locality        VARCHAR(255),      -- Ortsname
  sub_locality    VARCHAR(255),      -- Stadtteil
  geojson         JSONB,             -- GeoJSON-Geometrie
  description     TEXT,
  paper_id        UUID               -- Verweis auf zugehörige Vorlage
);
```

---

### System (`system`)

OParl-System-Endpunkt (Wurzel der API).

```sql
CREATE TABLE system (
  id                    UUID PRIMARY KEY,
  -- OParl-Basisfelder --
  oparl_version         VARCHAR(255) NOT NULL,  -- "https://schema.oparl.org/1.1/"
  name                  VARCHAR(512),
  contact_email         VARCHAR(255),
  contact_name          VARCHAR(255),
  website               TEXT,
  vendor                TEXT,
  product               TEXT,
  other_oparl_versions  TEXT[]
);
```

---

### Körperschaft (`body`)

Die kommunale Körperschaft (Gemeinde, Landkreis etc.).

```sql
CREATE TABLE body (
  id            UUID PRIMARY KEY,
  -- OParl-Basisfelder --
  system_id     UUID REFERENCES system(id) NOT NULL,
  location_id   UUID REFERENCES location(id),
  name          VARCHAR(512) NOT NULL,
  short_name    VARCHAR(255),
  website       TEXT,
  ags           VARCHAR(12),   -- Amtlicher Gemeindeschlüssel
  rgs           VARCHAR(16),   -- Regionalschlüssel
  equivalent    TEXT[],        -- Links zu äquivalenten Quellen
  contact_email VARCHAR(255),
  contact_name  VARCHAR(255),
  classification VARCHAR(255)  -- z.B. "Kreisfreie Stadt"
);
```

---

### Wahlperiode (`legislative_term`)

```sql
CREATE TABLE legislative_term (
  id        UUID PRIMARY KEY,
  -- OParl-Basisfelder --
  body_id   UUID REFERENCES body(id) NOT NULL,
  name      VARCHAR(512),       -- z.B. "Wahlperiode 2020-2025"
  start_date DATE,
  end_date   DATE
);
```

---

### Gremium (`organization`)

Ausschüsse, Fraktionen, Ämter.

```sql
CREATE TABLE organization (
  id                  UUID PRIMARY KEY,
  -- OParl-Basisfelder --
  body_id             UUID REFERENCES body(id),
  location_id         UUID REFERENCES location(id),
  name                VARCHAR(512) NOT NULL,
  short_name          VARCHAR(255),
  post                TEXT[],         -- Positionen im Gremium
  sub_organization_of UUID REFERENCES organization(id),
  organization_type   VARCHAR(255),   -- "committee", "fraction", "department"
  classification      VARCHAR(255),   -- z.B. "Hauptausschuss"
  start_date          DATE,
  end_date            DATE,
  website             TEXT,
  external_body       TEXT
);
```

---

### Person (`person`)

Mandatsträger und Verwaltungspersonal.

```sql
CREATE TABLE person (
  id              UUID PRIMARY KEY,
  -- OParl-Basisfelder --
  body_id         UUID REFERENCES body(id),
  location_id     UUID REFERENCES location(id),
  name            VARCHAR(512) NOT NULL,
  family_name     VARCHAR(255),
  given_name      VARCHAR(255),
  form_of_address VARCHAR(255),  -- Anrede
  affix           VARCHAR(255),  -- Namenszusatz
  title           TEXT[],
  gender          VARCHAR(50),
  phone           TEXT[],
  email           TEXT[],
  external_id     VARCHAR(255),  -- ID im Fremdsystem
  start_date      DATE,
  end_date        DATE,
  status          TEXT[]
);
```

---

### Mitgliedschaft (`membership`)

Zuordnung von Personen zu Gremien.

```sql
CREATE TABLE membership (
  id              UUID PRIMARY KEY,
  -- OParl-Basisfelder --
  organization_id UUID REFERENCES organization(id) NOT NULL,
  person_id       UUID REFERENCES person(id) NOT NULL,
  role            VARCHAR(255),         -- z.B. "Vorsitzender"
  voting_right    BOOLEAN DEFAULT true,
  start_date      DATE,
  end_date        DATE,
  on_behalf_of    UUID REFERENCES organization(id)
);
```

---

### Sitzung (`meeting`)

Ratssitzungen und Ausschusssitzungen.

```sql
CREATE TABLE meeting (
  id              UUID PRIMARY KEY,
  -- OParl-Basisfelder --
  body_id         UUID REFERENCES body(id),
  location_id     UUID REFERENCES location(id),
  name            VARCHAR(512),
  meeting_state   VARCHAR(100),    -- "eingeladen", "durchgeführt"
  cancelled       BOOLEAN DEFAULT false,
  start           TIMESTAMPTZ,
  "end"           TIMESTAMPTZ,
  invitation_id   UUID REFERENCES file(id),    -- Einladungs-PDF
  results_protocol_id UUID REFERENCES file(id), -- Ergebnisprotokoll
  verbatim_protocol_id UUID REFERENCES file(id), -- Wortprotokoll
  public          BOOLEAN DEFAULT true,
  is_series       BOOLEAN DEFAULT false,
  series_name     VARCHAR(512)
);
```

---

### Tagesordnungspunkt (`agenda_item`)

```sql
CREATE TABLE agenda_item (
  id              UUID PRIMARY KEY,
  -- OParl-Basisfelder --
  meeting_id      UUID REFERENCES meeting(id) NOT NULL,
  paper_id        UUID REFERENCES paper(id),
  number          VARCHAR(100),    -- z.B. "3.2"
  name            TEXT NOT NULL,
  public          BOOLEAN DEFAULT true,
  consultation_id UUID,
  result          TEXT,            -- Beschlussergebnis
  resolution_text TEXT,           -- Beschlusstext
  auxiliary_file  TEXT[],         -- Zusätzliche Dateien
  start           TIMESTAMPTZ,
  "end"           TIMESTAMPTZ
);
```

---

### Vorlage (`paper`)

Anträge, Beschlussvorlagen, Anfragen.

```sql
CREATE TABLE paper (
  id              UUID PRIMARY KEY,
  -- OParl-Basisfelder --
  body_id         UUID REFERENCES body(id),
  location_id     UUID REFERENCES location(id),
  main_file_id    UUID REFERENCES file(id),
  name            TEXT NOT NULL,
  reference       VARCHAR(255),    -- Aktenzeichen/Drucksachennummer
  date            DATE,
  paper_type      VARCHAR(255),    -- "Antrag", "Beschlussvorlage", "Anfrage"
  related_paper   TEXT[],
  superordinated_paper TEXT[],
  subordinated_paper   TEXT[],
  originator_person    TEXT[],
  under_direction_of   TEXT[],
  originator_organization TEXT[],
  consultation        TEXT[]
);
```

---

### Datei (`file`)

Dokumente und Anhänge.

```sql
CREATE TABLE file (
  id                    UUID PRIMARY KEY,
  -- OParl-Basisfelder --
  name                  VARCHAR(1024),
  file_name             VARCHAR(512),
  mime_type             VARCHAR(255),
  date                  DATE,
  size                  INTEGER,          -- Dateigröße in Bytes
  sha1_checksum         VARCHAR(40),
  sha512_checksum       VARCHAR(128),
  text                  TEXT,             -- Extrahierter Volltext
  access_url            TEXT,
  external_service_url  TEXT,
  download_url          TEXT,
  file_license          TEXT,
  storage_key           VARCHAR(1024)     -- Interner Speicherpfad
);
```

---

## Volltextsuche

```sql
-- GIN-Index für deutschsprachige Volltextsuche auf Vorlagen
CREATE INDEX paper_fts_idx ON paper
  USING GIN(to_tsvector(\german\, coalesce(name, \\) || \ \ || coalesce(reference, \\)));

-- GIN-Index für Datei-Volltext
CREATE INDEX file_text_fts_idx ON file
  USING GIN(to_tsvector(\german\, coalesce(text, \\)));
```

---

## Beziehungsdiagramm (vereinfacht)

```
system
  └── body (Körperschaft)
        ├── legislative_term (Wahlperiode)
        ├── organization (Gremium)
        │     └── membership ── person
        ├── meeting (Sitzung)
        │     └── agenda_item (TOP)
        │           └── paper (Vorlage)
        │                 └── file (Dokument)
        └── location (Ort)
```

---

## Hinweise zur Datenbank-Verwaltung

- **Migration starten:** `alembic upgrade head` im `/opt/aitema/ratsinformationssystem/backend`-Verzeichnis
- **Status prüfen:** `alembic current`
- **Rücksetzen:** `alembic downgrade -1`
- **OParl-Konformität:** Alle Felder folgen dem OParl 1.1 JSON-Schema (`https://schema.oparl.org/1.1/`)

Stand: Februar 2026
