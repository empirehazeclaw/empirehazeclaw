# VPS OpenClaw Setup - Wissensbasis

## Zusammenfassung
Nico baut eine KI-Agentenflotte auf Hostinger VPS mit Ubuntu 25.04.

## 🖥️ VPS Spezifikationen
- **Anbieter**: Hostinger
- **OS**: Ubuntu 25.04 (plucky)
- **RAM**: 4 GB
- **IP**: 187.124.11.27 / Tailscale: 100.119.249.42
- **SSH Port**: 22
- **User**: tim (mit sudo)

## ✅ Erfolgreiche Schritte
1. Docker installiert (hello-world: working)
2. Firewall konfiguriert (UFW: 22, 80, 443)
3. User `tim` erstellt mit sudo-Rechten
4. Docker-Gruppe für User `tim` eingerichtet
5. Clawdbot Container installiert (Python FastAPI)
6. Telegram Bot eingerichtet
7. Agent-Scripts: healer, attack_detector, load_balancer, memory_optimizer, mesh_controller
8. Watchdog installiert (openclaw-watchdog.service)
9. Tailscale installiert (serve mode)

## ❌ Bekannte Probleme & Lösungen

### Problem 1: OpenClaw Installation auf Python 3.13
- **Fehler**: `TOMLDecodeError` bei pip install -e .
- **Lösung**: pyproject.toml muss [project] Block enthalten

### Problem 2: Editable Install Fehler
- **Fehler**: `ModuleNotFoundError: No module named 'openclaw'`
- **Lösung**: Immer aus ~/openclaw/src installieren, nicht aus ~/openclaw

### Problem 3: Gateway Token Probleme
- **Fehler**: "device signature invalid", "1006 abnormal closure", ECONNREFUSED
- **Lösung**: openclaw gateway install --force

### Problem 4: Port 18789 belegt
- **Lösung**: lsof -i :18789, kill -9 <PID>

### Problem 5: Docker Permission denied
- **Fehler**: permission denied ... docker.sock
- **Lösung**: sudo usermod -aG docker tim

### Problem 6: JSON Config Fehler
- **Fehler**: "agents.list.0.tools: Unrecognized key: 'sessions'"
- **Lösung**: openclaw doctor --fix

### Problem 7: Gateway ECONNREFUSED
- **Lösung**: systemctl --user restart openclaw-gateway

### Problem 8: Watchdog Restart Loop
- **Symptom**: Prozesse mehrfach gestartet, tailscale serve --bg Loops
- **Lösung**: Restart=on-failure, RestartSec=15, KillMode=control-group

### Problem 9: SSH Connection closed (Tailscale gestoppt)
- **Ursache**: SSH lief über Tailscale VPN
- **Lösung**: Nie tailscaled auf VPS stoppen wenn SSH darüber läuft
- **Recovery**: Hostinger Console → systemctl start tailscaled

## 📋 Korrekte Installationsreihenfolge

```bash
# 1. User erstellen
useradd -m -s /bin/bash tim
usermod -aG sudo tim
usermod -aG docker tim

# 2. Docker
curl -fsSL https://get.docker.com | bash

# 3. Firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# 4. Swap (für 4GB RAM VPS)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 5. OpenClaw (nach Python Setup)
cd ~/openclaw/src
pip install -e . --config-settings editable_mode=compat

# 6. Gateway starten
openclaw gateway start

# 7. Tailscale (NACH verify SSH funktioniert!)
curl -fsSL https://tailscale.com/install.sh | sh
```

## 🔐 Stabiles Gateway Service Setup

```ini
[Unit]
Description=OpenClaw Gateway Stable Runtime
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/node /home/tim/.npm-global/lib/node_modules/openclaw/dist/index.js gateway --port 18789
Restart=on-failure
RestartSec=15
KillMode=control-group
Environment=HOME=/home/tim
Environment=OPENCLAW_GATEWAY_PORT=18789

[Install]
WantedBy=default.target
```

## 🚫 WARNUNGEN

1. **Niemals** tailscaled stoppen wenn SSH darüber läuft
2. **Niemals** pkill -9 auf VPS verwenden (kann SSH blockieren)
3. **Immer** erst prüfen ob Prozess root gehört
4. **Backup-SSH** ohne Tailscale einrichten

## 📦 Agent Scripts erstellt
- healer_agent.py - Self-Healing
- attack_detector.py - Security Monitoring
- load_balancer.py - CPU/RAM Throttling
- memory_optimizer.py - Cache Cleanup
- mesh_controller.py - Container Mesh
- telegram_bot.py - Telegram Connector

## 📅 Timeline
- 2026-02-27: Docker Installation erfolgreich
- 2026-03-02: OpenClaw VPS Setup, Clawdbot Container, Telegram Bot
- 2026-03-02: Watchdog installiert, Tailscale aktiviert
- 2026-03-02: SSH-Connection verloren (tailscaled gestoppt)

## Nächste Schritte
1. Per Hostinger Console wiederherstellen
2. Stabiles Gateway Setup aktivieren
3. Backup-SSH ohne Tailscale einrichten
