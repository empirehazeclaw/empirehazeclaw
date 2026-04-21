# Todo 2026-04-10

## Cleanup Tasks (from System Audit)
- [ ] 3.3 MB archive/2026-03.md löschen — LCM hat alles vollständig
- [ ] Wiki-Index Duplikate bereinigen (249 Duplikate, auto-regeneriert ab 21:00 UTC)
- [ ] Knowledge Graph relations vs relationships genauer prüfen (Audit war teilweise falsch)

## Previous P0 Results (already done)
- ✅ Semantic Index dedup (460 KB gespart)
- ✅ Rollback-Verzeichnis existiert nicht (Audit-Fehler)

## Discord Multi-Agent Setup (2026-04-10)

### Status: Phase 2 — Offen

| Component | Status | Was fehlt |
|-----------|--------|-----------|
| Discord Thread Bindings (Konzept) | ✅ Geforscht | — |
| CEO Discord Bot | ✅ Aktiv | — |
| Builder Discord Bot | ❌ Fehlt | Eigenen Bot Token erstellen |
| Security Discord Bot | ❌ Fehlt | Eigenen Bot Token erstellen |
| Data Discord Bot | ❌ Fehlt | Eigenen Bot Token erstellen |
| QC Discord Bot | ❌ Fehlt | Eigenen Bot Token erstellen |
| Research Discord Bot | ❌ Fehlt | Eigenen Bot Token erstellen |

### Was zu tun ist:
1. [ ] Discord Developer Portal → 5 neue Bot-Applikationen erstellen (Builder, Security, Data, QC, Research)
2. [ ] Jeden Bot in Discord Server/Forums einladen
3. [ ] threadBindings Config pro Bot in openclaw.json
4. [ ] Session Keys: `agent:builder:discord:...`, `agent:security:discord:...` etc.

### Voraussetzungen (Nico muss machen):
- 5x Discord Bot Tokens via https://discord.com/developers/applications

