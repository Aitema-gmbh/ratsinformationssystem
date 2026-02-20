# ALLRIS Import – Anleitung

## Uebersicht

Dieses Verzeichnis enthaelt Beispiel-Exportdateien aus dem ALLRIS-System
sowie eine Anleitung zum Import in das aitema|Rats RIS.

## Dateibeschreibung

| Datei | Inhalt | Trennzeichen |
|-------|--------|--------------|
| `allris_sitzungen.csv` | Sitzungen / Meetings | Semikolon (;) |
| `allris_vorlagen.csv` | Vorlagen / Drucksachen (Papers) | Semikolon (;) |
| `allris_personen.csv` | Personen / Mandatstraeger | Semikolon (;) |

Alle Dateien sind UTF-8 kodiert.

---

## CSV-Struktur

### allris_sitzungen.csv

| Spalte | OParl-Feld | Pflicht | Hinweis |
|--------|-----------|---------|---------|
| `sitzung_id` | – | ja | Eindeutige ALLRIS-ID |
| `gremium` | `organization.name` | ja | Muss Organisation in DB existieren |
| `sitzungsart` | `meeting.name` | nein | z.B. "Oeffentlich" |
| `datum` | `meeting.start` | ja | Format: DD.MM.YYYY |
| `uhrzeit_von` | `meeting.start` | nein | Format: HH:MM |
| `uhrzeit_bis` | `meeting.end` | nein | Format: HH:MM |
| `raum` | `location.room` | nein | |
| `strasse` | `location.street_address` | nein | |
| `ort` | `location.locality` | nein | PLZ + Ort |
| `status` | `meeting.meeting_state` | nein | Durchgefuehrt → completed |
| `einladung_url` | `meeting.invitation` | nein | URL zum Dokument |
| `protokoll_url` | `meeting.results_protocol` | nein | URL zum Protokoll |
| `bemerkung` | – | nein | Wird ignoriert |

### allris_vorlagen.csv

| Spalte | OParl-Feld | Pflicht | Hinweis |
|--------|-----------|---------|---------|
| `vorlage_id` | – | ja | Eindeutige ALLRIS-ID |
| `drucksachen_nr` | `paper.reference` | nein | Drucksachennummer |
| `titel` | `paper.name` | ja | |
| `vorlagenart` | `paper.paper_type` | nein | Beschlussvorlage / Antrag / Anfrage / Mitteilung |
| `datum` | `paper.date` | nein | Format: DD.MM.YYYY |
| `gremium` | `consultation.organization` | nein | |
| `sitzung_id` | FK zu `allris_sitzungen.sitzung_id` | nein | Erstellt Consultation |
| `verfasser` | `paper.originator_organizations` | nein | Name der Organisation |
| `status` | – | nein | Nur informativ |
| `hauptdokument_url` | `paper.main_file` | nein | Erstellt File-Objekt |
| `anlage_urls` | `paper.auxiliary_files` | nein | Pipe-getrennt (\|) |
| `schlagworte` | `paper.keyword` | nein | Semikolon-getrennt |

### allris_personen.csv

| Spalte | OParl-Feld | Pflicht | Hinweis |
|--------|-----------|---------|---------|
| `person_id` | – | ja | Eindeutige ALLRIS-ID |
| `anrede` | `person.form_of_address` | nein | Herr / Frau / Divers |
| `titel` | `person.title` | nein | Dr., Prof., etc. |
| `vorname` | `person.given_name` | ja | |
| `nachname` | `person.family_name` | ja | |
| `fraktion` | `membership.organization` | nein | Kurzname der Fraktion |
| `funktion` | `membership.role` | nein | Buergermeister, Stadtrat, etc. |
| `email` | `person.email` | nein | |
| `telefon` | `person.phone` | nein | |
| `status` | – | nein | Aktiv / Ausgeschieden |
| `adresse_strasse` | `location.street_address` | nein | |
| `adresse_plz` | `location.postal_code` | nein | |
| `adresse_ort` | `location.locality` | nein | |
| `geburtsjahr` | – | nein | Wird nicht importiert |
| `bemerkung` | – | nein | Wird ignoriert |

---

## Import-Reihenfolge

Wegen Abhaengigkeiten MUSS in dieser Reihenfolge importiert werden:

```
1. allris_personen.csv   → Personen & Memberships
2. allris_sitzungen.csv  → Meetings & Locations
3. allris_vorlagen.csv   → Papers, Files & Consultations
```

---

## Status-Mapping

### Sitzungs-Status

| ALLRIS-Wert | OParl `meeting_state` |
|-------------|----------------------|
| Geplant | `scheduled` |
| Eingeladen | `invited` |
| Laufend | `running` |
| Durchgefuehrt | `completed` |
| Abgesagt | `cancelled` |

### Vorlagen-Art

| ALLRIS-Wert | OParl `paper_type` |
|-------------|-------------------|
| Beschlussvorlage | `Beschlussvorlage` |
| Antrag | `Antrag` |
| Anfrage | `Anfrage` |
| Mitteilung | `Mitteilung` |
| Dringlichkeitsvorlage | `Beschlussvorlage` |
| Kenntnisnahme | `Mitteilung` |

---

## Ausfuehren des Imports

```bash
# Auf dem Server (in der Backend-Umgebung):
cd /opt/aitema/ratsinformationssystem/backend

# Einzeln:
python -m app.importers.allris_import \
    --file ../data/allris-import-example/allris_personen.csv \
    --type personen \
    --tenant musterstadt

python -m app.importers.allris_import \
    --file ../data/allris-import-example/allris_sitzungen.csv \
    --type sitzungen \
    --tenant musterstadt

python -m app.importers.allris_import \
    --file ../data/allris-import-example/allris_vorlagen.csv \
    --type vorlagen \
    --tenant musterstadt
```

---

## Hinweise

- **Duplikat-Erkennung**: Der Importer prueft `drucksachen_nr` bzw. `sitzung_id`
  auf Existenz und ueberspringt bereits vorhandene Eintraege (Upsert-Modus).
- **Dokumente**: URLs werden als `File`-Objekte mit `access_url` gespeichert.
  Eine tatsaechliche Archivierung erfordert einen separaten Download-Schritt.
- **Kodierung**: Exportdateien aus ALLRIS oft in Latin-1 – bitte vor dem
  Import in UTF-8 konvertieren: `iconv -f latin1 -t utf8 datei.csv > datei_utf8.csv`
- **Fraktionen**: Muessen vor dem Personen-Import als Organisationen angelegt sein.

---

## Eigene ALLRIS-Exporte erstellen

In ALLRIS NET (Version 3.x) koennen Exporte ueber:

```
Verwaltung > Export > CSV-Export
```

erstellt werden. Die Spalten-Reihenfolge kann abweichen – passen Sie
in diesem Fall das Import-Skript `backend/app/importers/allris_import.py`
entsprechend an.

---

*Letzte Aktualisierung: 2026-02-20*
*Kontakt: support@aitema.de*
