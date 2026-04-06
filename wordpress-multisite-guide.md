# WordPress Multisite Installations-Guide für EmpireHazeClaw

## Ziel
4 Domains mit einer WordPress Installation verwalten:
- empirehazeclaw.com (Corporate EN)
- empirehazeclaw.de (Corporate DE)
- empirehazeclaw.store (Shop)
- empirehazeclaw.info (Blog)

---

## Optionen

### Option A: WordPress Multisite (EMPFOHLEN)
Eine Installation, 4 Domains. Einfach zu warten.

### Option B: 4 Separate Installationen
4 separate WordPress Installationen. Mehr Wartung, aber mehr Kontrolle.

### Option C: Statische Seiten (AKTUELL)
Was wir jetzt haben - funktioniert, aber kein CMS.

---

## Empfehlung: Multisite

### Vorteile
- Eine Installation
- Ein Update für alle
- Einfache Verwaltung
- Geteilte Plugins/Themes
- Separate Verwaltung pro Site

### Nachteile
- Komplexeres Setup
- Alle teilen gleiche Ressourcen

---

## Schritt-für-Schritt: Multisite Installation

### Phase 1: Vorbereitung

#### 1.1 WordPress Container stoppen (falls aktiv)
```bash
docker stop wordpress_wordpress_1
docker stop wordpress_db_1
```

#### 1.2 Datenbank vorbereiten
```bash
# Neue Datenbank für Multisite
docker exec -it wordpress_db_1 mysql -u root -pwordpress -e "CREATE DATABASE wordpress;"
docker exec -it wordpress_db_1 mysql -u root -pwordpress -e "GRANT ALL PRIVILEGES ON wordpress.* TO 'wordpress'@'%';"
docker exec -it wordpress_db_1 mysql -u root -pwordpress -e "FLUSH PRIVILEGES;"
```

### Phase 2: WordPress Installation (Browser)

#### 2.1 Installation starten
Im Browser: `http://SERVER_IP:8890`

#### 2.2 Sprachauswahl
- Sprache: **Deutsch**
- Weiter

#### 2.3 Anmeldedaten
```
Site Name: EmpireHazeClaw
Benutzername: admin
Passwort: [STARKES_PASSWORT]
E-Mail: empirehazeclaw@gmail.com
```

#### 2.4 Multisite aktivieren
Nach Login in wp-config.php einfügen:
```php
define( 'WP_ALLOW_MULTISITE', true );
```

### Phase 3: Multisite einrichten

#### 3.1 Netzwerk-Setup
- Gehe zu: Werkzeuge → Netzwerk einrichten
- Netzwerk-Name: EmpireHazeClaw Network
- Netzwerk-Admin E-Mail: empirehazeclaw@gmail.com

#### 3.2 Subdomains vs Subdirectories
**Empfehlung: Subdomains**
- empirehazeclaw.com → Hauptseite
- de.empirehazeclaw.com → Deutsch
- store.empirehazeclaw.com → Shop
- blog.empirehazeclaw.com → Blog

ODER mit不同的 Domains (komplexer):
- Domain Mapping Plugin nutzen

#### 3.3 .htaccess ersetzen
WordPress gibt Dir den Code.

### Phase 4: Domain Mapping (für 4 separate Domains)

#### 4.1 Plugin installieren
**WordPress MU Domain Mapping**
- Plugin: "WordPress MU Domain Mapping"
- Oder: "Multiple Domain Mapping on Single Site"

#### 4.2 Domains zuweisen
```
Site 1: empirehazeclaw.com → Main
Site 2: empirehazeclaw.de → German
Site 3: empirehazeclaw.store → Shop
Site 4: empirehazeclaw.info → Blog
```

### Phase 5: DNS Konfiguration

#### 5.1 A-Records bei Ionos
```
@       A       SERVER_IP
www     A       SERVER_IP
de      A       SERVER_IP
store   A       SERVER_IP
blog    A       SERVER_IP
```

#### 5.2 Nginx Proxy (falls nötig)
Siehe unten.

---

## Alternative: 4 Separate Installationen

### Option A: 4 Docker Container

```bash
# COM (Port 8891)
docker run -d --name wp-com \
  -p 8891:80 \
  -e WORDPRESS_DB_HOST=wp_db_1 \
  -e WORDPRESS_DB_NAME=wp_com \
  -e WORDPRESS_DB_USER=wordpress \
  -e WORDPRESS_DB_PASSWORD=wordpress \
  wordpress:latest

# DE (Port 8892)
docker run -d --name wp-de \
  -p 8892:80 \
  -e WORDPRESS_DB_HOST=wp_db_2 \
  -e WORDPRESS_DB_NAME=wp_de \
  -e WORDPRESS_DB_USER=wordpress \
  -e WORDPRESS_DB_PASSWORD=wordpress \
  wordpress:latest
```

### Option B: 4 Datenbanken, 1 Container

```bash
# 4 Datenbanken erstellen
docker exec -it wordpress_db_1 mysql -u root -p
CREATE DATABASE wp_com;
CREATE DATABASE wp_de;
CREATE DATABASE wp_store;
CREATE DATABASE wp_info;
```

---

## Nginx Reverse Proxy Setup

### Nginx Config für Multisite

```nginx
# /etc/nginx/sites-available/empirehazeclaw

# COM
server {
    server_name empirehazeclaw.com www.empirehazeclaw.com;
    location / {
        proxy_pass http://localhost:8890;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# DE
server {
    server_name empirehazeclaw.de www.empirehazeclaw.de;
    location / {
        proxy_pass http://localhost:8890;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# STORE
server {
    server_name empirehazeclaw.store www.empirehazeclaw.store;
    location / {
        proxy_pass http://localhost:8890;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# INFO
server {
    server_name empirehazeclaw.info www.empirehazeclaw.info;
    location / {
        proxy_pass http://localhost:8890;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Empfohlene Plugins

### Must-Have
| Plugin | Zweck |
|--------|-------|
| Yoast SEO | Suchmaschinen-Optimierung |
| Elementor | Page Builder |
| Elementor Header Footer Builder | Header/Footer |
| Wordfence | Security |
| WP Super Cache | Caching |
| UpdraftPlus | Backups |
| Contact Form 7 | Kontaktformulare |
| Table of Contents Plus | Automatische Inhaltsverzeichnisse |

### Für Multisite
| Plugin | Zweck |
|--------|-------|
| Multisite Plugin Manager | Plugins network-wide verwalten |
| Domain Mapping | Domain-Zuweisung |

---

## Theme Empfehlungen

### Kostenlos
- Astra (schnell, flexibel)
- OceanWP
- GeneratePress

### Premium (empfohlen)
- Astra Pro
- OceanWP Pro
- Divi

### Mit Dark Mode
- Die meisten modernen Themes unterstützen Dark Mode

---

## Content Migration

### Von statischen Seiten importieren

#### 1. Blog Posts
Unsere Posts sind in:
```
/home/clawbot/.openclaw/workspace/blog/
/home/clawbot/.openclaw/workspace/projects/landing-pages/info/posts/
```

#### 2. eBooks
```
/home/clawbot/.openclaw/workspace/projects/landing-pages/info/downloads/
```

#### 3. Import
- WordPress Import Plugin
- Oder manuell kopieren

---

## Backup Strategy

### Vor dem Start
```bash
# Docker Volumes sichern
docker run --rm -v wordpress_db_data:/data -v $(pwd):/backup ubuntu tar czf /backup/wordpress_db_backup.tar.gz /data

# WordPress Files sichern
docker cp wordpress_wordpress_1:/var/www/html /backup/wordpress_files
```

### Nach Installation
- UpdraftPlus konfigurieren
- Automatische Backups: Täglich
- Aufbewahrung: 30 Tage

---

## Wartung

### Regelmäßige Tasks
| Task | Häufigkeit |
|------|------------|
| Updates prüfen | Täglich |
| Backups prüfen | Täglich |
| Security Scan | Wöchentlich |
| Performance | Monatlich |
| Database Optimize | Monatlich |

### Updates
```bash
# Docker Update
docker-compose pull
docker-compose up -d

# Oder im WordPress Backend
```

---

## Troubleshooting

### Häufige Probleme

#### 1. Weiße Seite (WSOD)
- WP_DEBUG in wp-config.php aktivieren
- Plugin Conflict: Alle Plugins deaktivieren

#### 2. 404 Fehler
- Permalinks neu speichern
- .htaccess prüfen

#### 3. Login funktioniert nicht
- Browser Cache löschen
- Cookies erlauben

#### 4. Bilder werden nicht angezeigt
- Upload Ordner Rechte: 755
- Datei Rechte: 644

---

## Checkliste vor Start

- [ ] Alle 4 Domains auf Server zeigen
- [ ] Datenbank vorbereitet
- [ ] SSL Zertifikate (Let's Encrypt)
- [ ] Backup Lösung bereit
- [ ] Theme gewählt
- [ ] Plugins ausgewählt

---

## Quick Start (Kurzversion)

1. **Im Browser installieren:** `http://IP:8890`
2. **Multisite aktivieren:** `define('WP_ALLOW_MULTISITE', true);`
3. **Netzwerk einrichten:** Werkzeuge → Netzwerk
4. **Domains zuweisen:** Domain Mapping Plugin
5. **Content importieren**

---

## Nächste Schritte

Nach Installation:
1. Theme installieren
2. Dark Mode aktivieren
3. Plugins installieren
4. Content hochladen
5. SEO einrichten

---

*Erstellt: 2026-03-15*
*Für: EmpireHazeClaw*
