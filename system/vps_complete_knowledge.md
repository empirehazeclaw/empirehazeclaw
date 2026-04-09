# VPS OpenClaw Setup - Complete Knowledge Base

## Overview
Nico builds an AI agent system on Hostinger VPS with Ubuntu 25.04 for: Research, Social Media (Instagram/TikTok), Print-on-Demand, Memory, Verification, Security.

## VPS Specifications
- **Provider**: Hostinger
- **OS**: Ubuntu 25.04 (plucky)
- **RAM**: 4 GB
- **IP**: 187.124.11.27 / Tailscale: 100.119.249.42
- **SSH Port**: 22
- **User**: tim (sudo)

## Completed Steps
1. Docker installed (hello-world: working)
2. Firewall configured (UFW: 22, 80, 443)
3. User `tim` created with sudo + docker groups
4. Clawdbot container installed (Python FastAPI)
5. Telegram Bot configured
6. Agent scripts: healer, attack_detector, load_balancer, memory_optimizer, mesh_controller
7. Watchdog installed (openclaw-watchdog.service)
8. Tailscale installed (serve mode)

## Problems & Solutions

### Problem 1: OpenClaw Installation on Python 3.13
- **Error**: `TOMLDecodeError` at pip install -e .
- **Solution**: pyproject.toml needs [project] block

### Problem 2: Editable Install Error
- **Error**: `ModuleNotFoundError: No module named 'openclaw'`
- **Solution**: Always install from ~/openclaw/src, not ~/openclaw

### Problem 3: Gateway Token Problems
- **Error**: "device signature invalid", "1006 abnormal closure", ECONNREFUSED
- **Solution**: openclaw gateway install --force

### Problem 4: Port 18789 Already in Use
- **Solution**: lsof -i :18789, kill -9 <PID>

### Problem 5: Docker Permission Denied
- **Error**: permission denied ... docker.sock
- **Solution**: sudo usermod -aG docker tim

### Problem 6: JSON Config Error
- **Error**: "agents.list.0.tools: Unrecognized key: 'sessions'"
- **Solution**: openclaw doctor --fix

### Problem 7: Gateway ECONNREFUSED
- **Solution**: systemctl --user restart openclaw-gateway

### Problem 8: Watchdog Restart Loop
- **Symptom**: Multiple processes started, tailscale serve --bg loops
- **Solution**: Restart=on-failure, RestartSec=15, KillMode=control-group

### Problem 9: SSH Connection Closed (Tailscale stopped)
- **Cause**: SSH ran over Tailscale VPN
- **Solution**: Never stop tailscaled if SSH runs over it
- **Recovery**: Hostinger Console → systemctl start tailscaled

## Correct Installation Sequence
```bash
# 1. User
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

# 4. Swap (for 4GB RAM VPS)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 5. OpenClaw
cd ~/openclaw/src
pip install -e . --config-settings editable_mode=compat
openclaw gateway start

# 6. Tailscale (AFTER verify SSH works!)
curl -fsSL https://tailscale.com/install.sh | sh
```

## Stable Gateway Service Setup
```ini
[Unit]
Description=OpenClaw Gateway Stable Runtime
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/node .../openclaw/dist/index.js gateway --port 18789
Restart=on-failure
RestartSec=15
KillMode=control-group
Environment=HOME=/home/tim
Environment=OPENCLAW_GATEWAY_PORT=18789

[Install]
WantedBy=default.target
```

## WARNINGS
1. **Never** stop tailscaled if SSH runs over it
2. **Never** use pkill -9 on VPS (can block SSH)
3. **Always** check if process belongs to root
4. **Set up** Backup-SSH without Tailscale

## Created Agent Scripts
- healer_agent.py - Self-Healing
- attack_detector.py - Security Monitoring
- load_balancer.py - CPU/RAM Throttling
- memory_optimizer.py - Cache Cleanup
- mesh_controller.py - Container Mesh
- telegram_bot.py - Telegram Connector
- watchdog.sh - Service Monitoring

## AI Agent System Architecture (Secure Autonomous Personal Assistant)

### Core Components
1. **Master Orchestrator** - Policy Engine, controls workflow, risk thresholds
2. **Research Agent** - Web search, trend analysis, source weighting
3. **Verification Agent** - Fact validation, risk scoring (0-1), consensus
4. **Social Media Agent** - Instagram/TikTok, engagement prediction
5. **Print-on-Demand Agent** - Design, trademark/copyright scanning
6. **Memory System** - Short-term (cache) + Long-term (Vector DB)
7. **Logging & Backup System** - Immutable ledger, hash chain, auto-rollback
8. **Security Layer** - Prompt injection shield, anomaly detection

### Risk Score Logic
- > 0.85 → Auto-Approve
- 0.6-0.85 → Warning Mode
- < 0.6 → Human Review

### Trust Score Formula
```
trust_score = 0.5 * source_credibility + 0.3 * consensus_score + 0.2 * domain_stability
```

### Decision Matrix
| Trust Score | Action |
|-------------|--------|
| > 0.85 | auto_approve |
| 0.6-0.85 | warning_mode |
| < 0.6 | human_review |

## Files Created
- knowledge/vps_openclaw_setup.md
- knowledge/ai_agent_system_v1.json
- knowledge/agent_implementation_v1.json
- knowledge/agent_implementation_code.py

## Timeline
- 2026-02-27: Docker Installation successful
- 2026-03-02: OpenClaw VPS Setup, Clawdbot Container, Telegram Bot
- 2026-03-02: Watchdog installed, Tailscale activated
- 2026-03-02: SSH-Connection lost (tailscaled stopped)
- 2026-03-02: Recovery via Hostinger Console

## Next Steps
1. Recover via Hostinger Console
2. Activate stable Gateway Setup
3. Set up Backup-SSH without Tailscale
4. Install Agent Implementation Code on VPS
