# SKILL VETTING WORKFLOW — Sicherheits-Prüfung für Skills

**Stand:** 2026-04-10

---

## 🎯 Prinzip

**ClawHub ist eine Black Box.** Wir vertrauen dem Code nicht blind.

1. **Lesen** → Was macht der Skill?
2. **Analysieren** → Welche Risiken?
3. **Manuell erstellen** → Nur sichere Teile übernehmen
4. **Testen** → In Sandbox bevor Production

---

## 🔍 Workflow

### Schritt 1: ClawHub durchsuchen
```bash
npx clawhub search <keyword>
```

### Schritt 2: Skill-Info abrufen
```bash
npx clawhub info <skill-name>
```

### Schritt 3: Code MANUELL inspizieren
```bash
# NICHT installieren! Stattdessen:
npx clawhub fetch <skill-name> --out /tmp/skill-inspect/
```

### Schritt 4: Security-Checkliste

| Check | Was prüfen |
|-------|------------|
| **Permissions** | Welche Tools/Commands werden genutzt? |
| **Network** | Sendet der Code Daten nach außen? |
| **Secrets** | API-Keys hardcoded? |
| **Dependencies** | Externe npm/Python Packages? |
| **File System** | Liest/schreibt der Code außerhalb workspace? |
| **Exec** | Führt arbitrary code aus? |

### Schritt 5: Manuell Skills erstellen
- Nur die FUNKTIONALITÄT übernehmen
- Nicht den Code kopieren
- eigene Implementierung schreiben

### Schritt 6: Testen in Sandbox
- Erst in isolierter Umgebung testen
- Gateway nicht beeinflussen

---

## 🚫 Niemals

- `npx clawhub install` direkt ausführen
- Code blind vertrauen
- API-Keys im Skill-Code belassen
- Unbekannte npm Packages installieren

---

## 📋 Security Red Flags

| Red Flag | Aktion |
|----------|--------|
| `fetch()` ohne Validierung | Sofort reject |
| Hardcoded API-Keys | löschen,换成 env vars |
| `child_process.exec()` mit user input | Reject |
| Dateien außerhalb workspace | Reject |
| Externe Netzwerk-Calls zu unknown hosts | Reject |
| npm Package von unbekanntem Author | Reject |

---

## ✅ Checkliste vor Installation

- [ ] Code manuell inspiziert
- [ ] Keine Red Flags gefunden
- [ ] Permissions minimal gehalten
- [ ] Test in Sandbox bestanden
- [ ] Nico über Risiken informiert (falls vorhanden)

---

*Erstellt: 2026-04-10 — Als sicherer Skill-Workflow*

---

## ✅ WORKFLOW TEST (2026-04-10)

**Skill getestet:** `knowledge-graph-skill`

### Ergebnis:

| Check | Result | Notes |
|-------|--------|-------|
| ClawHub Security Flag | ⚠️ SUSPICIOUS | Skill hat Security-Warnung |
| package.json | ✅ CLEAN | Zero external dependencies |
| install.mjs | ❌ RISK | Modifiziert SOUL.md, path traversal |
| graph.mjs | ✅ CLEAN | Local FS only, kein exec |
| vault.mjs | ✅ CLEAN | Standard crypto, kein network |

### Fazit:
**NICHT INSTALLIEREN** — install.mjs ist invasive und riskant.

### Workflow funktioniert:
1. ✅ `npx clawhub search` — funktioniert
2. ✅ `npx clawhub inspect --files` — zeigt Dateien
3. ✅ `npx clawhub inspect --file <path>` — liest einzelne Dateien
4. ✅ Security-Analyse möglich

---

*Test abgeschlossen: 2026-04-10 18:30 UTC*
