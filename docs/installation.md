# Installation – aitema|Rats RIS

## Voraussetzungen

- Docker ≥ 24.0
- Docker Compose ≥ 2.0
- Mindestens 4 GB RAM (Volltext-Suche benötigt mehr Speicher)
- Mindestens 20 GB Festplattenspeicher (für Dokumente und Protokolle)
- Eine Domain mit SSL-Zertifikat (für Produktionsbetrieb)

## Schnellstart (ca. 30 Minuten)

### 1. Repository klonen

```bash
git clone https://github.com/Aitema-gmbh/ratsinformationssystem.git
cd ratsinformationssystem
```

### 2. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
nano .env  # Passwörter und Domain anpassen
```

Mindestens diese Werte müssen gesetzt werden:

| Variable | Beschreibung | Beispiel |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL-Verbindungsstring | `postgresql://aitema:pass@db:5432/ris` |
| `NEXT_PUBLIC_BASE_URL` | Öffentliche URL | `https://ris.gemeinde.de` |

### 3. Starten

```bash
docker compose up -d
```

### 4. Öffnen

http://localhost:3000

## OParl-Import

aitema|Rats unterstützt den Import von Ratsdaten über die OParl-Schnittstelle:

```bash
# OParl-Endpunkt konfigurieren
OPARL_API_URL=https://ris.andere-gemeinde.de/oparl/v1.1

# Import starten
docker compose exec backend python manage.py import_oparl
```

## Produktionsbetrieb

### SSL-Zertifikat mit Let's Encrypt (Nginx)

```nginx
server {
    listen 443 ssl;
    server_name ris.ihre-gemeinde.de;

    ssl_certificate /etc/letsencrypt/live/ris.ihre-gemeinde.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ris.ihre-gemeinde.de/privkey.pem;

    # Erhöhtes Limit für Dokumenten-Uploads
    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
certbot --nginx -d ris.ihre-gemeinde.de
```

## Datensicherung

```bash
# Datenbank täglich sichern
0 2 * * * docker exec ris_db pg_dump -U aitema ris > /backup/ris-$(date +%Y%m%d).sql

# Hochgeladene Dokumente sichern
0 3 * * * rsync -av /opt/aitema/ratsinformationssystem/data/ /backup/ris-dokumente/

# Backups 30 Tage aufbewahren
0 4 * * * find /backup -name "ris-*.sql" -mtime +30 -delete
```

## Updates

```bash
git pull
docker compose pull
docker compose exec backend python manage.py migrate
docker compose up -d
```

## Häufige Probleme

### Migration schlägt fehl

```bash
docker compose logs backend
docker compose exec backend python manage.py showmigrations
```

### Volltextsuche findet keine Ergebnisse

```bash
docker compose exec backend python manage.py rebuild_index
```

### Speicher erschöpft

```bash
# RAM-Verbrauch prüfen
docker stats
# Volltext-Suche deaktivieren falls nötig
# ENABLE_FULLTEXT_SEARCH=false in .env setzen
```

## Support

Bei Fragen: [GitHub Issues](https://github.com/Aitema-gmbh/ratsinformationssystem/issues)
oder per E-Mail: kontakt@aitema.de
