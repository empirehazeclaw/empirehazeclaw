# Security Pre-Build Audit Workflow

**Version:** 1.0  
**Datum:** 2026-04-09  
**Owner:** Security Officer  

---

## 🎯 Ziel

Bevor Änderungen am System oder Code ausgeführt werden, muss der Builder sicherstellen, dass keine sicherheitsrelevanten Risiken entstehen. Dieser Workflow definiert, wann eine Security-Review erforderlich ist.

---

## ⚡ Wann ist eine Security Review Pflicht?

Eine Review ist **PFLICHT** bei:

| Kategorie | Beispiele |
|-----------|-----------|
| **Secrets/Keys** | API Keys, Tokens, Passwörter, Zugangsdaten |
| **Destructive Commands** | `rm -rf`, `dd`, `mkfs`, destructive `>` redirects |
| **Gateway/Auth Config** | Änderungen an `openclaw.yaml`, Auth-Modi, Discord-Config |
| **External APIs** | Neue HTTP-Aufrufe nach außen, Webhooks, Callback-URLs |
| **File Permissions** | `chmod 777`, `chown`, ACL-Änderungen auf `/etc/`, `/home/` |
| **System Timers** | Crontab-Änderungen, systemd timer, at-jobs |

---

## 📊 Risk Score System

### 🟢 LOW — Keine direkte Sicherheitsrelevanz
- Reine Leszugriffe
- Dokumentationsänderungen
- Nicht-sensitive Config-Änderungen
- **Aktion:** Builder kann direkt fortfahren

### 🟡 MEDIUM — Kurze Prüfung erforderlich
- Änderungen an nicht-sensitiven Configs
- Neue Dependencies (ohne Systemzugriff)
- Temporary file operations
- **Aktion:** Security Officer kurze Prüfung (async)

### 🔴 HIGH — CEO muss genehmigen
- Änderungen an Secrets, Keys, Tokens
- Destructive commands jeglicher Art
- Auth/Gateway Config-Änderungen
- External API-Aufrufe mit sensiblen Daten
- File permission-Änderungen auf sensitive Verzeichnisse
- Crontab/System timer Änderungen
- **Aktion:** Security Officer Review → CEO explizite Genehmigung

---

## 🔄 Workflow Ablauf

```
Builder plant Änderung
        │
        ▼
┌───────────────────────┐
│ Security Review       │
│ erforderlich?         │
└───────────────────────┘
        │
   JA   │   NEIN
    ┌───┴───┐
    ▼       ▼
 🟡/🔴    🟢 LOW
    │       │
    ▼       ▼
Security  Builder
Officer   fährt fort
Review
    │
    ▼
🔴 HIGH?
    │
   JA │  NEIN
    ┌─┴─┐
    ▼   ▼
 CEO  Security
Geneh- Officer
migung gibt frei
    │
    ▼
Builder fährt fort
```

---

## 📝 Review Request erstellen

Template: `/home/clawbot/.openclaw/workspace/security/templates/security_review_request.md`

**Pflichtfelder:**
- Änderungsübersicht
- Security-relevante Kategorien (ja/nein)
- Risk Score Bewertung
- Begründung

---

## 👥 Verantwortlichkeiten

| Role | Verantwortung |
|------|---------------|
| **Builder** | Review-Antrag erstellen, bei HIGH auf CEO-Genehmigung warten |
| **Security Officer** | MEDIUM prüfen, HIGH vorauswerten, CEO informieren |
| **CEO** | Finale Genehmigung bei HIGH Risk |

---

## 🚨 Emergency例外

Bei **akuten Sicherheitsvorfällen** (0-day, active breach) kann der Security Officer sofortige Maßnahmen ohne vorherige Genehmigung einleiten. Nachträgliche Dokumentation ist Pflicht.

---

## 📋 Checkliste für Builder

- [ ] Änderung identifiziert
- [ ] Risk Score bestimmt
- [ ] Security Review Request ausgefüllt (bei MEDIUM/HIGH)
- [ ] Auf Genehmigung gewartet (bei HIGH)
- [ ] Änderung dokumentiert

---

*Zuletzt aktualisiert: 2026-04-09 17:52 UTC*
