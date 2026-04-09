# Lektion 8: Error Handling & Recovery

## 🎯 Lernziel
Verstehe wie du mit Fehlern umgehst, Recovery-Strategien implementierst und wann du eskalierst. Fehler sind unvermeidlich — Downtime ist optional.

---

## 8.1 Das Gesetz

```
"Fehler passieren.
 Was zählt ist wie du damit umgehst."
```

### Fehler-Kategorien

| Kategorie | Beispiel | Handhabung |
|-----------|---------|------------|
| **Transient** | Netzwerk-Timeout | Retry |
| **Permanent** | Falsches Passwort | Fix the input |
| **Environmental** | Port belegt | Behebe Zustand |
| **Systemic** | Bug im Code | Fix oder Workaround |

---

## 8.2 Retry mit Exponential Backoff

### Das Prinzip

```javascript
// ❌ BAD: Einfacher Retry
for (let i = 0; i < 3; i++) {
  try { return doSomething(); }
  catch (e) { /* next attempt immediately */ }
}

// ✅ GOOD: Exponential Backoff
async function retryWithBackoff(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (e) {
      const waitTime = Math.pow(2, i) * 1000; // 1s, 2s, 4s
      if (i < maxRetries - 1) {
        await sleep(waitTime);
      }
    }
  }
  throw new Error("All retries failed");
}
```

### Retry-Algorithmen

| Name | Wartezeit | Gut für |
|------|-----------|--------|
| Fixed | 1s, 1s, 1s | Vorhersehbare Systeme |
| Linear | 1s, 2s, 3s | Weniger aggressive |
| **Exponential** | 1s, 2s, 4s, 8s | Netzwerk/Netzwerk |
| Jitter | Random +/- 0-1s | Race-Condition Vermeidung |

---

## 8.3 Timeout-Handling

### Warum Timeouts?

```
Ohne Timeout:
  Request gestartet...
  Server antwortet nicht...
  Wartet... wartet... wartet...
  FÜR IMMER!
```

### Timeout-Setzen

```javascript
// HTTP-Request mit Timeout
const response = await fetch(url, {
  signal: AbortSignal.timeout(5000) // 5 Sekunden
});

// exec mit Timeout
exec({ command: "find /", timeout: 30 }); // 30 Sekunden

// sessions_send mit Timeout
sessions_send({ message, timeoutSeconds: 120 });
```

### Timeout-Typen

| Typ | Typischer Wert | Verwendung |
|-----|----------------|------------|
| Short | 5-10s | Schnelle Operationen |
| Medium | 30-60s | Normale Tasks |
| Long | 120-300s | Komplexe Tasks |
| Infinite | ∞ | **Niemals!** |

---

## 8.4 Graceful Degradation

### Das Prinzip

```
Hauptsystem funktioniert nicht?
→ Nutze Fallback
→ Zeige reduzierte Funktionalität
→ Informiere User
→ Versuche nicht das ganze System zu crashen
```

### Beispiel

```javascript
async function getUserData(userId) {
  // Primär: Cache
  const cached = await cache.get(userId);
  if (cached) return cached;
  
  // Fallback 1: Datenbank
  try {
    const dbData = await db.query(userId);
    await cache.set(userId, dbData);
    return dbData;
  } catch (e) {
    // Fallback 2: Default-Wert
    return { name: "Unknown", status: "fallback" };
  }
}
```

---

## 8.5 Circuit Breaker Pattern

### Das Problem

```
Service A ──► Service B
              │
              ▼
           FAILING
              
A wartet auf B... Timeout...
A wartet auf B... Timeout...
A wartet auf B... Timeout...
A IST AUCH BLOCKIERT!
```

### Die Lösung: Circuit Breaker

```
Zustand: CLOSED (normal)
   │
   ├─► Failures > Threshold
   │       │
   │       ▼
   │    Zustand: OPEN (gebrochen)
   │       │
   │       └─► Nach Pause: HALF-OPEN
   │               │
   │               ├─► Success: CLOSED
   │               └─► Fail: OPEN
   │
   └─► Success: Reset counter
```

### Implementierung

```javascript
class CircuitBreaker {
  constructor(threshold = 5, timeout = 60000) {
    this.state = 'CLOSED';
    this.failures = 0;
    this.threshold = threshold;
    this.timeout = timeout;
  }
  
  async call(fn) {
    if (this.state === 'OPEN') {
      throw new Error('Circuit is OPEN');
    }
    
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (e) {
      this.onFailure();
      throw e;
    }
  }
  
  onSuccess() {
    this.failures = 0;
    this.state = 'CLOSED';
  }
  
  onFailure() {
    this.failures++;
    if (this.failures >= this.threshold) {
      this.state = 'OPEN';
      setTimeout(() => this.state = 'HALF-OPEN', this.timeout);
    }
  }
}
```

---

## 8.6 Error Recovery

### Recovery-Strategien

| Strategie | Wann nutzen | Beispiel |
|-----------|-------------|---------|
| **Retry** | Transient failures | Netzwerk-Timeout |
| **Restart** | Memory leaks, stuck processes | MetaClaw crash |
| **Rollback** | Bad deployment | Config-Fehler |
| **Failover** | Hardware-Ausfall | Sekundärer Server |
| **Fallback** | Teil-System-Down | Cache statt DB |
| **Escalate** | Nicht lösbar | Human eingreifen |

---

## 8.7 Panic-Modus

### Wann?

```
🔴 KRITISCHE FEHLER:
- Gateway startet nicht
- Alle Sessions down
- Datenkorruption entdeckt
- Security-Breach
```

### Panic-Protokoll

```
1. STOP — Keine weiteren Aktionen
2. INFORM — Sofort Nico informieren
3. DOCUMENT — Was ist passiert?
4. WAIT — Auf Anweisungen warten
5. DON'T FIX — NICHT selbst reparieren ohne Genehmigung
```

---

## 8.8 Logging für Errors

### Error-Log Struktur

```json
{
  "timestamp": "2026-04-08T17:45:00Z",
  "level": "ERROR",
  "agent": "builder",
  "task": "backup-script",
  "error": {
    "type": "PermissionDenied",
    "code": "EACCES",
    "message": "Cannot write to /opt/backups",
    "stack": "..."
  },
  "context": {
    "user": "root",
    "path": "/opt/backups",
    "operation": "write"
  }
}
```

### Log-Level

| Level | Bedeutung | Beispiel |
|-------|-----------|----------|
| DEBUG | Entwicklungs-Debug | "Entering function X" |
| INFO | Normaler Betrieb | "Backup started" |
| WARN | Potential problem | "Cache miss" |
| ERROR | Fehler | "Connection refused" |
| FATAL | System-Down | "Gateway crashed" |

---

## 8.9 Escalation

### Wann escalieren?

```
⏳ Situation nicht lösbar nach:
- 3 Retry-Versuchen
- 10 Minuten debugging
- Verstehen was passiert ist

→ ESCALATE!
```

### Escalation-Prozess

```
1. Problem dokumentieren (was, wann, wo, Fehlermeldung)
2. Checkpoints setzen (was wurde versucht)
3. An CEO/Nico: "Brauche Hilfe bei X"
4. Nicht abbrechen oder aufgeben
```

### Escalation-Nachricht

```
🔴 ESCALATION: Gateway startet nicht

Problem: Gateway mit Port 18789 fehlgeschlagen
Fehlermeldung: "Address already in use"

Was ich versucht habe:
1. Port geprüft — nmap zeigt nichts
2. Gateway-Status — bereits tot
3. Neustart — gleicher Fehler
4. Config-Validierung — OK

Stacktrace: [...]

Brauche Anweisung wie weiter.
```

---

## 8.10 Recovery-Playbook

### Schnell-Referenz

| Problem | Lösung |
|---------|--------|
| exec timeout | Retry mit Backoff, dann eskalieren |
| Gateway down | openclaw gateway restart |
| Port belegt | Prozess identifizieren, töten oder Gateway auf anderen Port |
| Config invalid | openclaw doctor --fix |
| Session stuck | Session killen, neu starten |
| Memory full | Archive alten Kontext, VACUUM |
| Cron hängt | Cron-Job manuell stoppen, Logs prüfen |
| AI-Model down | Fallback-Model nutzen |

---

## 📝 Zusammenfassung

| Konzept | Beschreibung |
|---------|--------------|
| Retry | Erneuter Versuch bei transienten Fehlern |
| Exponential Backoff | Längere Wartezeiten bei wiederholten Fehlern |
| Timeout | Obergrenze für Wartezeiten |
| Graceful Degradation | Fallback statt Total-Ausfall |
| Circuit Breaker | Verhindert Kaskaden-Fehler |
| Panic-Modus | Sofort stoppen, Nico informieren |
| Escalation | Hilfe anfordern wenn nicht lösbar |

---

## ✅ Checkpoint

- [ ] Was ist Exponential Backoff und warum nutzt man es?
- [ ] Warum sollte Timeouts niemals "unendlich" sein?
- [ ] Was ist Graceful Degradation?
- [ ] Wann sollte man NICHT selbst reparieren, sondern eskalieren?
- [ ] Was sind die 5 Recovery-Strategien?

---

*Lektion 8 — Error Handling & Recovery — Version 1.0*
