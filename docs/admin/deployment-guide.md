# aitema|Rats – Deployment Guide

> Version 1.0 | Februar 2026

## Inhaltsverzeichnis

1. [Systemanforderungen](#systemanforderungen)
2. [Docker Compose Setup](#docker-compose-setup)
3. [Erste Einrichtung](#erste-einrichtung)
4. [Demo-Daten laden](#demo-daten-laden)
5. [OParl API testen](#oparl-api-testen)
6. [Migration von ALLRIS/SessionNet](#migration)
7. [Monitoring & Backup](#monitoring--backup)
8. [Updates](#updates)

---

## Systemanforderungen

### Minimum (bis 50.000 Einwohner)

| Komponente | Anforderung |
|---|---|
| CPU | 2 vCPU |
| RAM | 4 GB |
| Speicher | 40 GB SSD |
| OS | Ubuntu 22.04+ / Debian 12+ |
| Docker | 24.0+ |
| Docker Compose | 2.20+ |

### Empfohlen (bis 200.000 Einwohner)

| Komponente | Anforderung |
|---|---|
| CPU | 4 vCPU |
| RAM | 8 GB |
| Speicher | 100 GB SSD |
| OS | Ubuntu 22.04+ / Debian 12+ |
| Docker | 24.0+ |
| Docker Compose | 2.20+ |

### Netzwerk

- Port 80/443 (HTTP/HTTPS) eingehend
- Port 5432 (PostgreSQL) nur intern
- Port 9200 (Elasticsearch) nur intern
- Oeffentliche Domain mit DNS-Eintrag

---

## Docker Compose Setup

### 1. Repository klonen

```bash
git clone https://github.com/aitema/rats.git /opt/aitema-rats
cd /opt/aitema-rats
```

### 2. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
nano .env
```

Wichtige Variablen:

```env
# Allgemein
DOMAIN=rats.musterstadt.de
ADMIN_EMAIL=admin@musterstadt.de

# Datenbank
POSTGRES_DB=aitema_rats
POSTGRES_USER=rats
POSTGRES_PASSWORD=<sicheres-passwort-generieren>

# Elasticsearch
ES_JAVA_OPTS=-Xms512m -Xmx512m

# OParl
OPARL_SYSTEM_ID=https://rats.musterstadt.de/oparl/v1
OPARL_BODY_NAME=Stadt Musterstadt

# SMTP
SMTP_HOST=mail.musterstadt.de
SMTP_PORT=587
SMTP_USER=rats@musterstadt.de
SMTP_PASSWORD=<smtp-passwort>
```

### 3. Docker Compose starten

```bash
docker compose up -d
```

Dies startet folgende Services:

| Service | Port | Beschreibung |
|---|---|---|
| `app` | 3000 | aitema\|Rats Anwendung |
| `postgres` | 5432 | PostgreSQL 16 Datenbank |
| `elasticsearch` | 9200 | Elasticsearch 8 Suchindex |
| `redis` | 6379 | Redis Cache & Sessions |
| `caddy` | 80, 443 | Reverse Proxy mit Auto-TLS |

### 4. Status pruefen

```bash
docker compose ps
docker compose logs -f app
```

Die Anwendung ist nach ca. 30 Sekunden unter `https://<DOMAIN>` erreichbar.

---

## Erste Einrichtung

### Admin-Account erstellen

```bash
docker compose exec app npx prisma db seed
```

Dies erstellt den initialen Admin-Account. Zugangsdaten werden in der Konsole ausgegeben.

### Mandanten konfigurieren

1. Unter `https://<DOMAIN>/admin` einloggen
2. Organisation anlegen (Name, Wappen, Kontaktdaten)
3. Gremien erstellen (Rat, Ausschuesse, Fraktionen)
4. Mandatstraeger importieren oder manuell anlegen
5. Sitzungskalender einrichten

---

## Demo-Daten laden

Fuer Test- und Evaluierungszwecke:

```bash
docker compose exec app node scripts/seed-demo.js
```

Dies laedt:
- 5 Gremien (Rat, 3 Ausschuesse, 1 Beirat)
- 35 Mandatstraeger mit Fraktionszuordnung
- 50 Sitzungen mit Tagesordnungen
- 120 Vorlagen mit Beispiel-PDFs
- Beschluesse und Abstimmungsergebnisse

---

## OParl API testen

Die OParl 1.1 API ist automatisch unter `/oparl/v1` verfuegbar.

### Endpunkte pruefen

```bash
# System-Endpunkt
curl https://<DOMAIN>/oparl/v1/system

# Bodies (Koerperschaften)
curl https://<DOMAIN>/oparl/v1/body

# Sitzungen
curl https://<DOMAIN>/oparl/v1/body/<body-id>/meeting

# Validierung
npx oparl-validator https://<DOMAIN>/oparl/v1/system
```

### OParl-Konformitaet

aitema|Rats besteht alle Tests des offiziellen OParl-Validators. Der Validator kann auch lokal ausgefuehrt werden:

```bash
docker compose exec app npm run oparl:validate
```

---

## Migration

### Von ALLRIS

```bash
# 1. ALLRIS-Datenbank-Export bereitstellen
cp allris-export.sql /opt/aitema-rats/migration/

# 2. Migrationsscript ausfuehren
docker compose exec app node scripts/migrate-allris.js \
  --source=/migration/allris-export.sql \
  --target-body=<body-id> \
  --dry-run

# 3. Nach Pruefung: Produktiv-Migration
docker compose exec app node scripts/migrate-allris.js \
  --source=/migration/allris-export.sql \
  --target-body=<body-id>
```

**Migriert werden:**
- Gremien und Mitgliedschaften
- Sitzungen mit Tagesordnungen
- Vorlagen und Beschluesse
- Dokumente und Anhaenge
- Personendaten

### Von SessionNet

```bash
# SessionNet stellt Daten per XML-Export bereit
docker compose exec app node scripts/migrate-sessionnet.js \
  --source=/migration/sessionnet-export/ \
  --target-body=<body-id> \
  --dry-run
```

### Migrations-Checkliste

- [ ] Daten-Export aus Altsystem erstellen
- [ ] Dry-Run durchfuehren und Mapping pruefen
- [ ] Testmigration in Staging-Umgebung
- [ ] Dokumentenintegritaet pruefen
- [ ] Parallelbetrieb starten (2-4 Wochen)
- [ ] Endgueltige Migration und DNS-Umstellung
- [ ] Altsystem deaktivieren

---

## Monitoring & Backup

### Health Check

```bash
# Anwendungs-Health
curl https://<DOMAIN>/api/health

# Elasticsearch-Status
curl http://localhost:9200/_cluster/health

# Datenbank-Verbindung
docker compose exec postgres pg_isready
```

### Automatische Backups

Backup-Script unter `/opt/aitema-rats/scripts/backup.sh`:

```bash
#\!/bin/bash
BACKUP_DIR=/opt/backups/aitema-rats
DATE=$(date +%Y%m%d_%H%M)

# PostgreSQL Dump
docker compose exec -T postgres pg_dump -U rats aitema_rats | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Dokumente sichern
tar -czf $BACKUP_DIR/docs_$DATE.tar.gz /opt/aitema-rats/data/documents/

# Alte Backups loeschen (aelter als 30 Tage)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Crontab einrichten:

```bash
# Taeglich um 2:00 Uhr
0 2 * * * /opt/aitema-rats/scripts/backup.sh
```

### Monitoring mit Prometheus (optional)

aitema|Rats exponiert Metriken unter `/metrics`:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: aitema-rats
    static_configs:
      - targets: ["localhost:3000"]
    metrics_path: /metrics
```

---

## Updates

### Managed (automatisch)

Updates werden im Managed-Tarif automatisch eingespielt. Sie werden vorab per E-Mail informiert.

### Self-Hosted

```bash
cd /opt/aitema-rats

# Aktuellen Stand sichern
docker compose exec -T postgres pg_dump -U rats aitema_rats > backup_before_update.sql

# Update ziehen
git pull origin main

# Container neu bauen und starten
docker compose pull
docker compose up -d --build

# Datenbank-Migrationen ausfuehren
docker compose exec app npx prisma migrate deploy

# Suchindex aktualisieren
docker compose exec app node scripts/reindex-elasticsearch.js
```

### Versionshinweise

Aenderungen werden im CHANGELOG.md dokumentiert. Fuer Major-Updates wird ein separater Migrationsleitfaden bereitgestellt.

---

## Haeufige Probleme

### Elasticsearch startet nicht

```bash
# vm.max_map_count erhoehen
sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" >> /etc/sysctl.conf
```

### Speicherplatz knapp

```bash
# Docker-Bereinigung
docker system prune -a --volumes

# Alte Logs loeschen
docker compose logs --no-log-prefix app | tail -1000 > /tmp/recent-logs.txt
```

### Zertifikat wird nicht ausgestellt

Stellen Sie sicher, dass:
- Die Domain korrekt auf den Server zeigt (A-Record)
- Port 80 und 443 erreichbar sind
- Keine Firewall den Zugriff blockiert

---

*Support: support@aitema.de | Dokumentation: https://docs.aitema.de/rats*
