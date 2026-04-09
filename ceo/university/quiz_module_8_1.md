# Quiz Modul 8.1: OpenClaw Deployment & Operations

## Quiz für Lektion 8.1 — OpenClaw Deployment & Operations

**Thema:** Deployment, Config-Management, Troubleshooting, Production Operations

**Gesamtpunktzahl:** 100 Punkte | **Bestehensgrenze:** 70 Punkte

---

## Teil A: Multiple Choice (40 Punkte — 4 Punkte pro Frage)

**1. Welcher Key ist in einer Agent-Definition der Haupt-Arbeitsbereich?**

a) `agentDir`
b) `workspace`
c) `home`
d) `workingDirectory`

<details>
<summary>Lösung</summary>
**Antwort: b) workspace** — Der `workspace` definiert das Arbeitsverzeichnis für Datei-Operationen.
</details>

---

**2. Was ist die Standard-Port des OpenClaw Gateways?**

a) 8080
b) 3000
c) 18789
d) 18792

<details>
<summary>Lösung</summary>
**Antwort: c) 18789** — Das Gateway läuft standardmäßig auf Port 18789.
</details>

---

**3. Welcher Auth-Modus ist am sichersten für Production?**

a) `none`
b) `token`
c) `open`
d) `allowall`

<details>
<summary>Lösung</summary>
**Antwort: b) token** — Token-basierte Authentifizierung ist sicherer als `none` oder `open`.
</details>

---

**4. Was bedeutet `bind: "loopback"` in der Gateway-Config?**

a) Gateway läuft ohne Passwort
b) Gateway ist nur über localhost erreichbar
c) Gateway startet automatisch neu
d) Gateway nutzt TLS

<details>
<summary>Lösung</summary>
**Antwort: b) Gateway ist nur über localhost erreichbar** — `loopback` bedeutet 127.0.0.1, kein externer Zugriff.
</details>

---

**5. Welcher Befehl validiert und repariert die openclaw.json?**

a) `openclaw config --validate`
b) `openclaw doctor --fix`
c) `openclaw validate --repair`
d) `openclaw check --auto`

<details>
<summary>Lösung</summary>
**Antwort: b) openclaw doctor --fix** — Der Doctor-Modus prüft und behebt Config-Probleme automatisch.
</details>

---

**6. Was ist der richtige Befehl um den Gateway-Status zu prüfen?**

a) `openclaw status`
b) `openclaw gateway status`
c) `openclaw system check`
d) `openclaw health`

<details>
<summary>Lösung</summary>
**Antwort: b) openclaw gateway status** — Zeigt Gateway-Laufzeit, Port, Auth-Status.
</details>

---

**7. Welches ist kein gültiger Session-Typ in OpenClaw?**

a) `main`
b) `isolated`
c) `subagent`
d) `temporary`

<details>
<summary>Lösung</summary>
**Antwort: d) temporary** — Gültige Typen sind: main, isolated, subagent, acp. `temporary` existiert nicht.
</details>

---

**8. Was tut `openclaw gateway restart`?**

a) Löscht alle Sessions und startet neu
b) Liest Config neu und startet Gateway-Prozess neu
c) Update das Gateway auf die neueste Version
d) Exportiert Gateway-Logs

<details>
<summary>Lösung</summary>
**Antwort: b)** — Gateway wird gestoppt, Config neu gelesen, Gateway wieder gestartet.
</details>

---

**9. Welcher Command ist korrekt um eine Datei zu sichern?**

a) `tar -czf backup.tar ~/.openclaw/workspace/`
b) `zip -r backup.zip ~/.openclaw/`
c) `cp -r ~/.openclaw/workspace /backup/`
d) Beide a) und c) sind korrekt

<details>
<summary>Lösung</summary>
**Antwort: d)** — Beide `tar` (komprimiert) und `cp` (einfach) funktionieren für Backups.
</details>

---

**10. Was ist die sicherste bind-Einstellung für Production?**

a) `0.0.0.0`
b) `loopback`
c) `192.168.1.1`
d) `any`

<details>
<summary>Lösung</summary>
**Antwort: b) loopback** — Bindet nur an localhost, kein externer Zugriff möglich.
</details>

---

## Teil B: True/False (20 Punkte — 4 Punkte pro Frage)

**11. Die `systemPrompt` Property kann direkt in der Agent-Config definiert werden.**

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: b) Falsch** — `systemPrompt` ist kein gültiger Key. Identity/Prompt kommt aus SOUL.md.
</details>

---

**12. `openclaw gateway stop` beendet den Gateway-Prozess vollständig.**

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: a) Wahr** — `stop` beendet den Gateway komplett. Mit `start` wieder starten.
</details>

---

**13. Der `dmPolicy: "allowlist"` erlaubt nur explizit erlaubte User-IDs.**

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: a) Wahr** — `allowlist` bedeutet nur explizit gelistete IDs dürfen DM senden.
</details>

---

**14. Backups können nur mit dem `tar`-Befehl erstellt werden.**

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: b) Falsch** — Auch `cp`, `rsync`, oder andere Backup-Tools funktionieren.
</details>

---

**15. Ein Health-Check-Script sollte bei Fehler einen Alert senden.**

a) Wahr
b) Falsch

<details>
<summary>Lösung</summary>
**Antwort: a) Wahr** — Health Checks dienen dazu, Probleme frühzeitig zu erkennen und zu melden.
</details>

---

## Teil C: Praxisfragen (40 Punkte)

**16. Du startest `openclaw gateway restart` und erhältst "Config invalid — agents.list.0: Unrecognized key". Was ist das Problem und wie behebst du es? (10 Punkte)**

<details>
<summary>Lösung</summary>
**Problem:** Ein ungültiger Key in der Agent-Config (z.B. `systemPrompt` existiert nicht).

**Behebung:**
1. `openclaw doctor --fix` ausführen
2. Oder manuell den ungültigen Key aus `openclaw.json` entfernen
3. Identity/System-Prompt kommt aus SOUL.md, nicht aus der Config
</details>

---

**17. Der Gateway startet nicht. Der Befehl `ss -tlnp | grep 18789` zeigt nichts. Was prüfst du zuerst und wie behebst du das Problem? (10 Punkte)**

<details>
<summary>Lösung</summary>
**Prüfen:**
1. `openclaw gateway status` — läuft der Gateway überhaupt?
2. Logs prüfen: `tail -f ~/.openclaw/logs/gateway.log`
3. Port belegt?: `netstat -tlnp | grep 18789`

**Behebung:**
- Wenn Port belegt: anderen Prozess stoppen oder Gateway auf anderen Port legen
- Wenn Config-Fehler: `openclaw doctor --fix`
- Wenn gestoppt: `openclaw gateway start`
</details>

---

**18. Du willst einen Backup-Job für alle Workspaces erstellen. Schreibe ein Bash-Script das:
- Workspaces nach `/opt/backups/openclaw/workspaces_YYYYMMDD.tar.gz` sichert
- Die Config nach `/opt/backups/openclaw/config_YYYYMMDD.json` sichert
- Nicht älter als 7 Tage ist (alte löschen)
(20 Punkte)**

<details>
<summary>Lösung</summary>
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/openclaw"
DATE=$(date +%Y%m%d)

# Backup-Verzeichnis erstellen
mkdir -p $BACKUP_DIR

# Config sichern
cp ~/.openclaw/openclaw.json $BACKUP_DIR/config_$DATE.json

# Workspaces sichern
tar -czf $BACKUP_DIR/workspaces_$DATE.tar.gz ~/.openclaw/workspace/

# Alte Backups löschen (>7 Tage)
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup erstellt: $(date)"
```
</details>

---

## Auswertung

| Punkte | Note |
|--------|------|
| 90-100 | 🌟 Exzellent |
| 80-89 | ✅ Sehr Gut |
| 70-79 | ✅ Bestanden |
| <70 | ❌ Nicht bestanden |

---

*Quiz erstellt: 2026-04-08*
