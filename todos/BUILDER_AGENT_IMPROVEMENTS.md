# Builder TODO - Agent Architecture Improvements
*Last updated: 2026-04-09 16:52 UTC*

## Status Legend
- [ ] To Do
- 🔄 In Progress
- ✅ Done
- ❌ Blocked

---

## Aufgabe 1: Dead Letter Queue für fehlgeschlagene Jobs
**Priority:** 🔴 Hoch
**Problem:** Fehlgeschlagene Crons eskalieren nicht automatisch.

**Action:** Failure Alert System in Cron-Jobs aktivieren
**Target:** Alle crontags mit `failureAlert` config erweitern

- [ ] Security Officer Daily Scan → failureAlert konfigurieren
- [ ] Data Manager Daily Audit → failureAlert konfigurieren
- [ ] Research Daily Roundup → failureAlert konfigurieren
- [ ] Builder Daily Build Report → failureAlert konfigurieren
- [ ] QC Officer Daily Validation → failureAlert konfigurieren

**Progress:**
- [ ] 2026-04-09: Initiiert

---

## Aufgabe 2: Alte Phoenix/Sovereign Jobs aufräumen
**Priority:** 🟡 Mittel
**Problem:** 5+ deaktivierte Jobs mit alten Namen verursachen Confusion.

**Action:** Deaktivierte/verwaiste Cron-Jobs identifizieren und löschen
**Jobs to remove:**
- [ ] Security - Phoenix Reschedule (id: b204feb7-...)
- [ ] Data - Phoenix Reschedule (id: f87c47dd-...)
- [ ] Builder - Sovereign One-Shot (id: 90d83804-...)
- [ ] Research - Phoenix Reschedule (id: 9416fd63-...)
- [ ] Data Manager - Sovereign One-Shot (id: 70bde24b-...)
- [ ] Security Officer - Sovereign Daily (id: 584f6e16-...)

**Progress:**
- [ ] 2026-04-09: Initiiert

---

## Aufgabe 3: Agent-Heartbeat-Netzwerk einführen
**Priority:** 🟡 Mittel
**Problem:** Kein Agent weiß ob ein anderer noch "lebendig" ist.

**Action:** Heartbeat-Log System implementieren
**Steps:**
- [ ] Verzeichnis erstellen: `/home/clawbot/.openclaw/workspace/system/heartbeats/`
- [ ] Heartbeat-Script pro Agent erstellen
- [ ] Cron für periodische Heartbeats einrichten

**Progress:**
- [ ] 2026-04-09: Initiiert

---

## Aufgabe 4: Peer-to-Peer Fallback-Kommunikation
**Priority:** 🟢 Niedrig
**Problem:** Bei CEO-Ausfall stoppt die gesamte Kommunikation.

**Action:** Direkte Agent-zu-Agent Kommunikation bei CEO-Ausfall
**Steps:**
- [ ] Backup-Routing für kritische Jobs definieren
- [ ] Alternative Delivery-Channels konfigurieren

**Progress:**
- [ ] 2026-04-09: Initiiert

---

## Aufgabe 5: Last-Verteilung auf CEO reduzieren
**Priority:** 🟡 Mittel
**Problem:** ~15 Cron-Jobs laufen durch CEO als Single Point of Failure.

**Action:** Direkte Agent-Assignment für wiederkehrende Jobs
**Jobs to reassign:**
- [ ] Security-Daily direkt an security_officer
- [ ] Data-Daily direkt an data_manager
- [ ] Research-Daily direkt an research

**Progress:**
- [x] 2026-04-09: Initiiert
- [x] 2026-04-09: Script erstellt + getestet ✅

---

## Abgeschlossen
✅ 2026-04-09: Peer-to-Peer Failover System implementiert