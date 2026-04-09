# OpenClaw Patch Notes

## Version: 2026.3.13
*Datum: 14.03.2026*

---

## 🆕 New Features

### Android/Chat Settings
- Redesign der Chat-Einstellungen
- Grouped Device und Media Sektionen
- Connect und Voice Tabs refreshed
- Dichteres Mobile Layout

### iOS/Onboarding
- First-run Welcome Pager vor Gateway Setup
- Stoppt Auto-Öffnen des QR Scanners
- Zeigt /pair qr Anweisungen

### Browser/Existing-Session
- Official Chrome DevTools MCP attach mode
- Für signed-in live Chrome Sessions
- Docs für chrome://inspect/#remote-debugging

### Browser/Agents
- profile="user" für logged-in host browser
- profile="chrome-relay" für extension relay
- Agents können echten Browser bevorzugen

### Browser/Act Automation
- Batched actions
- Selector targeting
- Delayed clicks
- Normalized batch dispatch

### Docker/Timezone
- OPENCLAW_TZ Environment Variable
- Gateway und CLI können timezone pinnen

---

## 🔧 Fixes

### Dashboard/Chat UI
- Stoppt reloading full chat history bei jedem tool result
- Keine UI freeze/re-render storms mehr

### Gateway/Client Requests
- Reject unanswered RPC calls nach timeout
- Keine hängenden Promises mehr

### Build/Plugin-SDK
- Bundle plugin-sdk subpath entries in one pass
- Keine duplizierten chunks mehr

### Ollama/Reasoning
- Stoppt promoting native thinking/reasoning fields
- Keine internal thoughts im reply

### Android/Onboarding QR
- Wechsel zu Google Code Scanner
- Zuverlässiger als ZXing

### Browser/Existing-Session
- Harder driver validation
- Transport errors trigger reconnects
- ARIA role sets deduplicated

### Control UI/Insecure Auth
- Preserves shared token und password auth
- LAN sessions funktionieren

### Gateway/Session Reset
- Preserves lastAccountId und lastThreadId
- Replies route zu same account/thread

### macOS/Onboarding
- Kein self-restart von launchd gateways
- Längere Zeit für health check

### Gateway/Status
- --require-rpc flag
- Klare Linux daemon-install failure reporting

### macOS/Exec Approvals
- Respects per-agent exec approval settings
- Gateway-triggered requests folgen policy

### Telegram/Media Downloads
- Thread transport policy into SSRF-guarded file fetches
- Inbound attachments keep working

### Telegram/IPv4 Fallback
- Retry once mit IPv4 fallback
- Funktioniert auf IPv6-broken hosts

### Windows/Gateway Install
- Bound schtasks calls
- Fallback zu Startup-folder

### Windows/Gateway Stop
- Resolve Startup-folder fallback listeners
- stop killt wirklich processes

### Windows/Gateway Status
- Reuse installed service command environment
- Reporting bleibt korrekt

### Windows/Gateway Auth
- Kein device identity auf loopback
- Keine stale signature errors

### Discord/Gateway Startup
- Transient startup errors werden behandelt
- Keine crashes mehr

### Slack/Probe
- Stable auth.test() bot und team metadata

### Dashboard/Chat UI
- Oversized plain-text replies als paragraphs
- Nicht mehr als gray code blocks

---

## 📦 Dependencies
- @mariozechner/pi-*: 0.58.0

---

*Gespeichert: 2026-03-14*
