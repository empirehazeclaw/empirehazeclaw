# Konzept: Fleet Commander (Der Watchdog für Managed AI Hosting)

Wenn wir 10, 50 oder 100 Kunden-VPS auf Hetzner hosten, können wir uns nicht manuell auf jeden Server per SSH einloggen, um zu prüfen, ob der Agent noch lebt oder abgestürzt ist. Wir brauchen eine zentrale Kommando-Brücke.

## 1. Die Architektur: Hub & Spoke
- **Hub (Wir):** EmpireHazeClaw Master-Server (Unser aktuelles System).
- **Spokes (Kunden):** Isolierte Hetzner VPS (z.B. `kunde1.empirehazeclaw.host`, `kunde2...`).

## 2. Der Heartbeat-Ping (Health Check)
Auf jedem Kunden-Server läuft ein winziges Python-Skript (`watchdog_client.py`), das alle 60 Sekunden einen "Heartbeat" (Lebenszeichen) an unseren Master-Server sendet:
```json
{
  "customer_id": "cx_12345",
  "status": "online",
  "agent_process_alive": true,
  "cpu_usage": 15.2,
  "ram_usage": 45.8,
  "errors_last_5m": 0
}
```

## 3. Der Fleet Commander (Unser Überwacher)
Auf unserem System bauen wir den `fleet_commander.py`. 
- Er sammelt alle Pings.
- **Auto-Restart:** Meldet sich ein Kunden-Server 5 Minuten lang nicht (oder `agent_process_alive` ist false), verbindet sich unser System via SSH-Key (oder Ansible) auf den Kunden-Server und führt automatisch einen `openclaw gateway restart` aus.
- **Alerts:** Schlägt der Restart dreimal fehl, schickt unser System eine Telegram-Nachricht an dich: *"🚨 KUNDE CX_12345 OFFLINE. MANUELLER EINGRIFF NÖTIG."*

## 4. Remote Updates & Deployments
Wenn wir ein Bugfix für den "Sales Agenten" schreiben, loggen wir uns nicht bei 50 Kunden ein. Wir pushen den Fix in unser privates Git-Repo. Der Fleet Commander loggt sich auf allen 50 Servern ein und führt `git pull && openclaw restart` aus.

---
**Zusammenfassung:**
Wir garantieren die Uptime für die Kunden nicht durch unsere Arbeitszeit, sondern durch einen zentralen "Watchdog", der alle Server pingt und bei Abstürzen selbstständig den Restart triggert, noch bevor der Kunde überhaupt merkt, dass sein Agent geschlafen hat.
