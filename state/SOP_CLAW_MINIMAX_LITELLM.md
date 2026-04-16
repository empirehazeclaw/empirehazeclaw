# SOP: Claw + MiniMax via Litellm Proxy
**Erstellt:** 2026-04-16  
**Ziel:** Claw CLI (claw) auf VPS mit MiniMax M2.7 als Model betreiben  
**Status:** ENTWURF — Evaluate & Improve BEFORE execution

---

## 🎯 Ziel

Claw CLI (`claw`) unterstützt nativ nur Anthropic API. MiniMax wird nicht direkt unterstützt.
→ Litellm Proxy als Vermittler: Claw → Litellm (localhost:4000) → MiniMax API

```
[Claw CLI] → [Litellm Proxy :4000] → [MiniMax API https://api.minimax.io/anthropic/v1/messages]
```

---

## 📋 PHASE 1: RESEARCH & EVALUATION

### Was ich weiss:
- MiniMax hat Anthropic-kompatiblen Endpoint: `https://api.minimax.io/anthropic/v1/messages`
- Litellm unterstützt MiniMax offiziell: `minimax/MiniMax-M2.1`
- Claw nutzt ANTHROPIC_API_KEY env var + standard Anthropic endpoint
- Claw kann auf eigenen Endpoint zeigen via `ANTHROPIC_BASE_URL`

### Unterstützte MiniMax Models via Litellm:
| Model | Input | Output | Prompt Caching |
|-------|-------|--------|----------------|
| MiniMax-M2.1 | $0.3/M | $1.2/M | Read $0.03/M, Write $0.375/M |
| MiniMax-M2.1-lightning | $0.3/M | $2.4/M | — |
| MiniMax-M2 | $0.3/M | $1.2/M | — |

**MiniMax-M2.7 ???** — Litellm listet M2.1, M2.1-lightning, M2. — **M2.7 nicht explizit**. Evtl. funktioniert es als Custom Model.

---

## 🔒 BACKUP & ROLLBACK STRATEGIE

### Backup Points (BEFORE any changes):
- [ ] 1. Full workspace backup (tar.gz)
- [ ] 2. OpenClaw config backup
- [ ] 3. Claw config backup (falls vorhanden: `~/.claw/`)
- [ ] 4. Litellm config snapshot (nach Installation, vor Konfiguration)
- [ ] 5. Systemd service file backup (falls vorhanden)

### Rollback Mechanismen:
| Risiko | Rollback |
|--------|----------|
| Litellm startet nicht | Docker/Service deaktivieren, Port 4000 frei, claw nutzt wieder direkt API |
| MiniMax Key funktioniert nicht | Key in config.yaml prüfen, ggf.回退 |
| Claw-Config kaputt | `~/.claw/` aus Backup zurückspielen |
| Gateway/OpenClaw betroffen | Backup zurückspielen, Service neustarten |

### Wichtige Constraints:
- **LITELLM_SALT_KEY** nicht ändern nach Installation (API Keys in DB verschlüsselt)
- **DISABLE_SCHEMA_UPDATE=true** setzen bei Helm/Migration-Setup
- Config-Änderungen **vor** Deployment testen

---

## 📝 PHASE 2: INSTALLATIONS-PLAN

### Schritt 1: Backup erstellen
```bash
# Workspace Full Backup
sudo tar -czf /home/clawbot/.openclaw/workspace/backups/workspace_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  /home/clawbot/.openclaw/workspace/ceo \
  /home/clawbot/.openclaw/workspace/memory/ \
  /home/clawbot/.openclaw/workspace/state/ \
  --exclude='*.node_modules' \
  --exclude='*.git' \
  2>/dev/null

# Claw config sichern
cp -r ~/.claw/ /home/clawbot/.openclaw/workspace/backups/claw_config_$(date +%Y%m%d)/

# OpenClaw auth-profiles sichern
cp /home/clawbot/.openclaw/agents/ceo/agent/auth-profiles.json \
  /home/clawbot/.openclaw/workspace/backups/auth-profiles.json.bak
```

### Schritt 2: Litellm installieren

**Option A: PIP (einfach, für Test)**
```bash
pip install litellm
# Test: litellm --version
```

**Option B: Docker (production recommended)**
```bash
# Docker installieren falls nicht vorhanden
apt-get update && apt-get install -y docker.io
systemctl enable docker

# Litellm Docker Image holen
docker pull ghcr.io/berriai/litellm:main-latest
```

### Schritt 3: Litellm Config erstellen
```yaml
# /home/clawbot/litellm_config.yaml
model_list:
  - model_name: MiniMax-M2.7
    litellm_params:
      model: minimax/MiniMax-M2.1
      api_key: os.environ/MINIMAX_API_KEY
      api_base: https://api.minimax.io/anthropic/v1/messages
      rpm: 60  # rate limit

general_settings:
  master_key: sk-litellm-proxy-key-change-me
  ui_access_mode: admin

environment_variables:
  MINIMAX_API_KEY: "DEIN_MINIMAX_API_KEY_HIER"
```

### Schritt 4: Config testen (VOR Service)
```bash
# Test ob MiniMax Key funktioniert
MINIMAX_API_KEY="DEIN_KEY" litellm --test

# Test ob Config valid ist
litellm --config /home/clawbot/litellm_config.yaml --test
```

### Schritt 5: Litellm Proxy starten
```bash
# Option A: Direkt (Test)
MINIMAX_API_KEY="DEIN_KEY" litellm --config /home/clawbot/litellm_config.yaml

# Option B: Systemd Service (production)
cat > /etc/systemd/system/litellm-proxy.service <<EOF
[Unit]
Description= LiteLLM Proxy
After=network.target

[Service]
Type=simple
User=clawbot
WorkingDirectory=/home/clawbot
ExecStart=/home/clawbot/opencl_env/bin/litellm --config /home/clawbot/litellm_config.yaml --port 4000
Restart=always
RestartSec=5
Environment=MINIMAX_API_KEY=DEIN_KEY

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable litellm-proxy
systemctl start litellm-proxy
systemctl status litellm-proxy
```

### Schritt 6: Claw umkonfigurieren
```bash
# Claw auf Litellm Endpoint zeigen lassen
export ANTHROPIC_BASE_URL="http://127.0.0.1:4000"
export ANTHROPIC_API_KEY="sk-litellm-proxy-key-change-me"

# Test
claw --model MiniMax-M2.7 prompt "hello"
```

**ODER** in `/home/clawbot/.claw/` eine config.yaml erstellen:
```yaml
# ~/.claw/config.yaml
providers:
  minimax:
    type: custom
    api_key: sk-litellm-proxy-key-change-me
    base_url: http://127.0.0.1:4000
```

### Schritt 7: Firewall anpassen
```bash
# Port 4000 nur local!
sudo ufw allow 4000/tcp from 127.0.0.1
sudo ufw deny 4000/tcp
sudo ufw status verbose
```

### Schritt 8: Verifizieren
```bash
# Healthcheck
curl http://127.0.0.1:4000/health

# Claw Test
claw --model MiniMax-M2.7 prompt "say hi in 10 words"

# Logs prüfen
journalctl -u litellm-proxy -f
```

---

## ⚠️ RISIKO-ANALYSE

| Risiko | Wahrscheinlichkeit | Auswirkung | Mitigation |
|--------|------------------|------------|------------|
| MiniMax M2.7 nicht unterstützt | Mittel | Niedrig | M2.1 als Fallback, Config anpassen |
| Port 4000 Konflikt | Niedrig | Mittel | Vor Start prüfen ob Port frei |
| Litellm stürzt ab | Niedrig | Mittel | Systemd auto-restart |
| API Key falsch | Mittel | Hoch | Key vor Start testen |
| Gateway/OvClaw beeinflusst | Sehr Niedrig | Hoch | Backup + Rollback bereit |
| Netzwerk-Firewall blockt | Niedrig | Hoch | Lokaler Loopback reicht für Claw |

---

## 🔄 ROLLBACK PROCEDURE

### Wenn etwas schiefgeht:
```bash
# 1. Litellm Service stoppen
sudo systemctl stop litellm-proxy
sudo systemctl disable litellm-proxy

# 2. Backup zurückspielen
sudo rm -rf /home/clawbot/.claw/
sudo cp -r /home/clawbot/.openclaw/workspace/backups/claw_config_[TIMESTAMP]/ /home/clawbot/.claw/

# 3. Alte config.yaml wiederherstellen falls vorhanden

# 4. Dienst neustarten
sudo systemctl restart openclaw-gateway
```

---

## ❓ OFFENE FRAGEN (vor execution klären)

1. **MiniMax M2.7 vs M2.1** — Ist M2.7 über Litellm erreichbar oder nur M2.1?
2. **Besteht bereits ein funktionierender MiniMax Key?** — Letzter Test zeigte HTTP 529 — Server-Problem oder Key-Problem?
3. **Docker vs PIP** — Was ist die bevorzugte Methode auf diesem VPS?
4. **Soll Claw permanent auf Litellm zeigen oder nur bei Bedarf?**

---

## ✅ CHECKLISTE VOR EXECUTION

- [ ] Backup vollständig erstellt
- [ ] MiniMax API Key getestet (direkt, nicht über Litellm)
- [ ] Risiko-Analyse reviewed
- [ ] Offene Fragen geklärt
- [ ] Rollback Procedure getestet (trocken)
- [ ] Nico hat zugestimmt

---

*Dieses Dokument ist ein lebender Standard. Bei jeder Änderung des Setup-Prozesses: Dokument aktualisieren, Backup erstellen, dann erst ausführen.*
