# Deployment-Anleitung: aitema|RIS

Vollstaendige Anleitung zur Installation des OParl-konformen Ratsinformationssystems fuer Kommunen.

## Systemvoraussetzungen

| Komponente | Mindest | Empfohlen |
|------------|---------|-----------|
| CPU | 2 vCPU | 4 vCPU |
| RAM | 4 GB | 8 GB |
| Speicher | 50 GB SSD | 200 GB SSD |
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |
| Docker | 24.0+ | 26.0+ |
| Docker Compose | 2.20+ | 2.27+ |
| Offene Ports | 80, 443 | 80, 443 |

> **Speicherbedarf:** Rechnen Sie je nach Dokumentenaufkommen mit 2-5 GB pro Jahr.
> Fuer grosse Kommunen (>50.000 EW) mindestens 100 GB SSD empfohlen.

---

## Installation in 5 Schritten

### Schritt 1: Server vorbereiten

```bash
# System aktualisieren
apt update && apt upgrade -y

# Docker installieren
curl -fsSL https://get.docker.com | sh
usermod -aG docker $USER

# Docker Compose Plugin
apt install docker-compose-plugin -y

# Hilfswerkzeuge
apt install -y git curl nano ufw dnsutils jq

# Firewall
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp
ufw enable
```

### Schritt 2: Repository klonen

```bash
mkdir -p /opt/kommunal && cd /opt/kommunal
git clone https://github.com/Aitema-gmbh/ratsinformationssystem.git
cd ratsinformationssystem
```

### Schritt 3: Konfiguration

```bash
cp .env.example .env
nano .env
```

Konfiguration in `.env`:

```env
# ================================================================
# PFLICHTFELDER
# ================================================================

# Domain (DNS muss auf diesen Server zeigen)
DOMAIN=ris.ihre-kommune.de

# Datenbankpasswort (openssl rand -hex 20)
POSTGRES_PASSWORD=SICHERES_DATENBANKPASSWORT

# JWT-Secret (openssl rand -hex 32)
JWT_SECRET=LANGER_ZUFAELLIGER_JWT_SCHLUESSEL

# ================================================================
# KOMMUNALE STAMMDATEN
# ================================================================

# Offizieller Name der Kommune fuer OParl
BODY_NAME=Stadt Musterhausen
BODY_SHORT_NAME=Musterhausen
BODY_WEBSITE=https://www.musterhausen.de
BODY_CONTACT_EMAIL=ris@musterhausen.de

# Amtlicher Gemeindeschluessel (AGS) - 8-stellig
BODY_AGS=09162000

# Bundesland-Kuerzel (z.B. BY, BW, NW, HE, ...)
BODY_STATE=BY

# ================================================================
# E-MAIL
# ================================================================

SMTP_HOST=smtp.musterhausen.de
SMTP_PORT=587
SMTP_USER=ris@musterhausen.de
SMTP_PASS=E-MAIL-PASSWORT
SMTP_TLS=true
FROM_EMAIL=ris@musterhausen.de
FROM_NAME=Ratsinformationssystem Musterhausen

# ================================================================
# OPTIONALE EINSTELLUNGEN
# ================================================================

# Sitzungsunterlagen: automatisch als PDF bereitstellen
AUTO_PDF_CONVERSION=true

# Maximale Dokumentengroesse in MB
MAX_FILE_SIZE_MB=100

# Zugelassene Dateitypen
ALLOWED_FILE_TYPES=pdf,docx,doc,xlsx,xls,pptx,ppt,odt,ods

# Volltext-Suche in Dokumenten (erfordert mehr RAM)
FULLTEXT_SEARCH=true

# Oeffentliche Tagesordnungen (vor der Sitzung sichtbar)
PUBLIC_AGENDA_HOURS_BEFORE=72

# OParl-Kompatibilitaetsmodus
OPARL_VERSION=1.1
```

### Schritt 4: Starten

```bash
# System starten
docker compose -f docker-compose.prod.yml up -d

# Logs beobachten
docker compose -f docker-compose.prod.yml logs -f --tail=50

# Status pruefen
docker compose -f docker-compose.prod.yml ps
```

Erwarteter Status:

```
NAME                STATUS          PORTS
ris-backend         Up (healthy)
ris-frontend        Up (healthy)
ris-db              Up (healthy)
ris-elasticsearch   Up (healthy)
ris-redis           Up (healthy)
traefik             Up              0.0.0.0:80->80, 0.0.0.0:443->443
```

### Schritt 5: DNS und erste Einrichtung

```bash
# DNS-Propagation pruefen
dig ris.ihre-kommune.de +short

# Admin-Account anlegen
docker compose -f docker-compose.prod.yml exec backend \
  python3 manage.py createsuperuser

# System-Validierung
curl https://ris.ihre-kommune.de/oparl/v1.1/system
```

---

## OParl-API konfigurieren

### OParl-Endpunkte

Das System implementiert den OParl 1.1 Standard vollstaendig:

| Endpunkt | URL | Beschreibung |
|----------|-----|--------------|
| System | `/oparl/v1.1/system` | Systeminfo und Koerperliste |
| Body | `/oparl/v1.1/body` | Kommunale Koerperschaften |
| Meeting | `/oparl/v1.1/meeting` | Sitzungen |
| AgendaItem | `/oparl/v1.1/agendaitem` | Tagesordnungspunkte |
| Paper | `/oparl/v1.1/paper` | Drucksachen |
| File | `/oparl/v1.1/file` | Dokumente/Dateien |
| Organization | `/oparl/v1.1/organization` | Gremien und Ausschuesse |
| Person | `/oparl/v1.1/person` | Ratsmitglieder |
| Membership | `/oparl/v1.1/membership` | Gremienzugehoerigkeiten |
| Location | `/oparl/v1.1/location` | Sitzungsorte |

### Gemeindeschluessel und Koerper einrichten

```bash
# Body-Objekt in Admin-UI anlegen:
# https://ris.ihre-kommune.de/admin/

# Oder per CLI:
docker compose -f docker-compose.prod.yml exec backend \
  python3 manage.py shell -c "
from ris.models import Body
Body.objects.create(
    name='Stadt Musterhausen',
    shortName='Musterhausen',
    website='https://www.musterhausen.de',
    ags='09162000',
    contactEmail='ris@musterhausen.de',
    licenseUrl='https://creativecommons.org/licenses/by/4.0/'
)
print('Body angelegt')
"
```

### OParl-Feed fuer externe Portale konfigurieren

```bash
# In .env - Zeitstempel fuer aendernde Objekte
OPARL_EXTERNAL_BODY_URL=https://ris.ihre-kommune.de/oparl/v1.1/
OPARL_CONTACT_URL=https://www.musterhausen.de/rathaus/stadtrat/
OPARL_CONTACT_NAME=Stadtrat Musterhausen

# API-Zugang fuer Aggregatoren (z.B. Politik-bei-uns)
OPARL_API_KEY_ENABLED=true
```

### OParl-Validierung

```bash
# System-Endpunkt validieren
curl -s https://ris.ihre-kommune.de/oparl/v1.1/system | jq .

# Body-Liste pruefen
curl -s https://ris.ihre-kommune.de/oparl/v1.1/body | jq '.data[].name'

# Sitzungen der letzten 30 Tage
curl -s "https://ris.ihre-kommune.de/oparl/v1.1/meeting?since=$(date -d '30 days ago' +%Y-%m-%d)" | jq '.data | length'

# Mit offiziellem OParl-Validator pruefen
# https://validator.oparl.org/
# URL eingeben: https://ris.ihre-kommune.de/oparl/v1.1/system
```

---

## Datenimport aus Altsystem

### Vorhandene Daten importieren

Das System unterstuetzt Import aus gaengigen RIS-Altsystemen:

**Methode A: CSV-Import (einfach)**

```bash
# CSV-Format-Vorlage exportieren
docker compose -f docker-compose.prod.yml exec backend \
  python3 manage.py export_import_template --format=csv

# CSV-Datei importieren
docker compose -f docker-compose.prod.yml exec backend \
  python3 manage.py import_csv \
    --type=meetings \
    --file=/data/sitzungen-export.csv \
    --encoding=utf-8
```

**Methode B: OParl-Import aus anderem RIS**

```bash
# Aus OParl-kompatiblem Quellsystem importieren
docker compose -f docker-compose.prod.yml exec backend \
  python3 manage.py import_oparl \
    --url=https://altes-ris.ihre-kommune.de/oparl/v1.0/system \
    --since=2020-01-01 \
    --dry-run  # Erst Testlauf ohne echten Import

# Nach Pruefung: echter Import
docker compose -f docker-compose.prod.yml exec backend \
  python3 manage.py import_oparl \
    --url=https://altes-ris.ihre-kommune.de/oparl/v1.0/system \
    --since=2020-01-01
```

**Methode C: Dokument-Massenimport**

```bash
# PDF-Dokumente aus Ordner importieren
docker cp /lokale/dokumente/. ris-backend:/tmp/import/

docker compose -f docker-compose.prod.yml exec backend \
  python3 manage.py import_documents \
    --path=/tmp/import/ \
    --type=paper \
    --year=2023
```

### Importstatus pruefen

```bash
# Importierte Datensaetze zaehlen
docker compose -f docker-compose.prod.yml exec backend \
  python3 manage.py shell -c "
from ris.models import Meeting, Paper, Person, Organization
print(f'Sitzungen: {Meeting.objects.count()}')
print(f'Drucksachen: {Paper.objects.count()}')
print(f'Personen: {Person.objects.count()}')
print(f'Gremien: {Organization.objects.count()}')
"

# Import-Log anzeigen
docker compose -f docker-compose.prod.yml logs backend | grep -i "import"
```

---

## Backup-Strategie

### Automatisches Backup

```bash
mkdir -p /backup/ris

cat > /usr/local/bin/ris-backup.sh << 'BACKUP_SCRIPT'
#!/bin/bash
set -e

BACKUP_DIR=/backup/ris
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=365  # 1 Jahr (kommunale Aufbewahrungspflicht!)

echo "[$(date)] Starte RIS-Backup..."

# 1. Kompletter Datenbank-Dump (inkl. alle Sitzungen, Beschluesse)
docker exec ris-db pg_dump -U postgres ris \
  | gzip > "$BACKUP_DIR/db-$DATE.sql.gz"

# 2. Alle Dokumente (Drucksachen, Protokolle)
docker run --rm --volumes-from ris-backend \
  -v "$BACKUP_DIR:/backup" alpine \
  tar czf "/backup/documents-$DATE.tar.gz" /app/media/

# 3. Elasticsearch-Index
docker exec ris-elasticsearch \
  curl -s -XPOST "localhost:9200/_snapshot/backup_repo/snapshot-$DATE" || true

# Groesse pruefen
echo "[$(date)] Backup: $(du -sh $BACKUP_DIR | cut -f1)"

# Alte Backups loeschen
find "$BACKUP_DIR" -name "*.gz" -mtime "+$RETENTION_DAYS" -delete
BACKUP_SCRIPT
chmod +x /usr/local/bin/ris-backup.sh

# Taeglich 02:30 Uhr
echo "30 2 * * * root /usr/local/bin/ris-backup.sh >> /var/log/ris-backup.log 2>&1" \
  > /etc/cron.d/ris-backup
```

### Wiederherstellung aus Backup

```bash
# System stoppen (ausser Datenbank)
docker compose -f docker-compose.prod.yml stop backend frontend

# Datenbank wiederherstellen
docker exec -i ris-db dropdb -U postgres ris
docker exec -i ris-db createdb -U postgres ris
zcat /backup/ris/db-DATUM.sql.gz | docker exec -i ris-db psql -U postgres ris

# Dokumente wiederherstellen
docker run --rm --volumes-from ris-backend \
  -v /backup/ris:/backup alpine \
  tar xzf /backup/documents-DATUM.tar.gz -C /

# System neu starten
docker compose -f docker-compose.prod.yml start backend frontend
```

---

## DSGVO-Hinweise

### Personenbezogene Daten im RIS

Das RIS verarbeitet folgende personenbezogene Daten:

| Datenkategorie | Betroffene | Rechtsgrundlage | Aufbewahrung |
|---------------|------------|-----------------|--------------|
| Namen von Ratsmitgliedern | Mandatstraeger | Art. 6 Abs. 1 lit. e DSGVO | Dauerhaft (oeffentliches Amt) |
| Abstimmungsverhalten | Ratsmitglieder | Art. 6 Abs. 1 lit. e DSGVO | Dauerhaft (Transparenz) |
| Kontaktdaten Verwaltung | Mitarbeiter | Art. 6 Abs. 1 lit. c DSGVO | Laufzeit Dienstverhältnis |
| Einwohnerdaten in Antraegen | Buerger | Art. 6 Abs. 1 lit. e DSGVO | Konfigurierbar |

### Nicht-oeffentliche Dokumente

```bash
# In Admin-UI: Dokumente als "nicht oeffentlich" markieren
# In .env:
NON_PUBLIC_DOCUMENT_ACCESS=admin,council  # Nur Admin und Ratsmitglieder

# Automatische Veroeffentlichung nach Ablauf Sperrfrist
AUTO_PUBLISH_AFTER_DAYS=30
```

### Datenschutzerklaerung anpassen

Die Datenschutzerklaerung wird unter `/datenschutz` angezeigt.
Anpassen in: Admin > Einstellungen > Rechtliche Texte

---

## Troubleshooting

### Suchergebnisse fehlen oder unvollstaendig

```bash
# Elasticsearch-Index neu aufbauen
docker compose -f docker-compose.prod.yml exec backend \
  python3 manage.py rebuild_index --noinput

# Elasticsearch-Status pruefen
curl http://localhost:9200/_cluster/health?pretty
```

### Dokument kann nicht angezeigt werden (PDF-Konvertierung)

```bash
# Konvertierungs-Queue pruefen
docker compose -f docker-compose.prod.yml exec backend \
  python3 manage.py shell -c "
from ris.tasks import pending_conversions
print(f'Ausstehende Konvertierungen: {pending_conversions()}')
"

# Konvertierung manuell neu starten
docker compose -f docker-compose.prod.yml exec backend \
  python3 manage.py convert_documents --retry-failed
```

### OParl-Validierungsfehler

```bash
# Fehlende Pflichtfelder finden
docker compose -f docker-compose.prod.yml exec backend \
  python3 manage.py validate_oparl --verbose

# Haeufige Fehler:
# - Body ohne AGS: In Admin > Koerperschaften > AGS eintragen
# - Meeting ohne Location: Sitzungsort anlegen und verknuepfen
# - Paper ohne File: Dokument hochladen oder Beschreibung ergaenzen
```

---

## Support

| Kanal | Kontakt |
|-------|---------|
| E-Mail | support@aitema.de |
| GitHub Issues | https://github.com/Aitema-gmbh/ratsinformationssystem/issues |
| OParl-Spec | https://oparl.org/spezifikation/ |
| Dokumentation | https://aitema.de/api-docs/ratsinformationssystem |

---

*Letzte Aktualisierung: Februar 2026 | aitema GmbH*
*OParl-Version: 1.1 | EUPL 1.2*
