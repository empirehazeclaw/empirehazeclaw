# MCP — Model Context Protocol Specification

**Version:** 1.0  
**Status:** Production Ready  
**Last Updated:** 2026-04-08

---

## Overview

MCP ist ein standardisiertes Protokoll für strukturierte Agent-zu-Agent Kommunikation in der EmpireHazeClaw Flotte. Es bietet Typisierte Schemas, Cycle Detection, Retry-Logik und ein einheitliches Message-Format.

---

## Message Format

```json
{
  "version": "1.0",
  "type": "tool_call | response | error | cascade",
  "source": "agent_name",
  "target": "agent_name",
  "payload": {
    "tool": "tool_name",
    "input": { /* typed schema */ },
    "output": { /* typed schema */ }
  },
  "metadata": {
    "traceId": "uuid-v4",
    "depth": 1,
    "retryCount": 0,
    "timestamp": "ISO-8601",
    "ttl": 64
  }
}
```

### Message Types

| Type | Beschreibung |
|------|--------------|
| `tool_call` | Anfrage einen Tool auszuführen |
| `response` | Ergebnis einer Tool-Ausführung |
| `error` | Fehler bei der Ausführung |
| `cascade` | Weiterleitung an anderen Agent |

---

## Cycle Detection

### Regeln

- **MAX_DEPTH**: 64 — Messages mit `depth > MAX_DEPTH` werden geblockt
- **DUPLICATE DETECTION**: Wenn gleicher `traceId` + gleicher `input` erkannt → blockieren

### Implementation

```
Jede Message erhält bei Erstellung:
  - traceId: UUID v4 (eindeutig pro Request-Kette)
  - depth: Inkrementiert bei jeder Weiterleitung

Bei Empfang:
  1. Prüfe depth > MAX_DEPTH → BLOCK
  2. Prüfe traceId + input in History → DUPLICATE
  3. Bei DUPLICATE: Sofort antworten ohne Neu-Ausführung
```

---

## Retry Logic

### Konfiguration

| Parameter | Wert |
|-----------|------|
| MAX_RETRIES | 3 |
| BACKOFF_BASE | 1000ms |
| BACKOFF_MULTIPLIER | 2 |
| BACKOFF_SEQUENCE | 1s, 2s, 4s |

### Exponential Backoff

```
Attempt 1: 1s warten
Attempt 2: 2s warten  
Attempt 3: 4s warten
Attempt 4+: MAX_RETRIES erreicht → ERROR
```

---

## Typed Schemas

### exec Schema

```json
{
  "tool": "exec",
  "input": {
    "command": { "type": "string", "required": true },
    "workdir": { "type": "string", "required": false },
    "timeout": { "type": "number", "required": false, "min": 1, "max": 300 },
    "env": { "type": "object", "required": false }
  },
  "output": {
    "stdout": { "type": "string" },
    "stderr": { "type": "string" },
    "exitCode": { "type": "number" },
    "duration": { "type": "number" }
  }
}
```

### write Schema

```json
{
  "tool": "write",
  "input": {
    "path": { "type": "string", "required": true, "pattern": "^/" },
    "content": { "type": "string", "required": true }
  },
  "output": {
    "success": { "type": "boolean" },
    "bytesWritten": { "type": "number" }
  }
}
```

### edit Schema

```json
{
  "tool": "edit",
  "input": {
    "path": { "type": "string", "required": true, "pattern": "^/" },
    "edits": {
      "type": "array",
      "required": true,
      "items": {
        "oldText": { "type": "string" },
        "newText": { "type": "string" }
      }
    }
  },
  "output": {
    "success": { "type": "boolean" },
    "editsApplied": { "type": "number" }
  }
}
```

### message Schema

```json
{
  "tool": "message",
  "input": {
    "action": { "type": "string", "required": true, "enum": ["send", "react", "delete", "edit"] },
    "channel": { "type": "string", "required": true },
    "target": { "type": "string", "required": false },
    "message": { "type": "string", "required": false },
    "media": { "type": "string", "required": false }
  },
  "output": {
    "success": { "type": "boolean" },
    "messageId": { "type": "string" }
  }
}
```

---

## Routing

### Agent Routing Table

| Agent | Session Key Pattern | Zuständigkeit |
|-------|---------------------|---------------|
| CEO | agent:ceo:* | Orchestration |
| Security | agent:security:* | Audits |
| Builder | agent:builder:* | Coding |
| Data | agent:data:* | Memory/DB |
| QC | agent:qc:* | Validation |

### Route Decision Matrix

```
Input → Analyse:
  ├─ Security Thema → Security Officer
  ├─ Data/Memory → Data Manager
  ├─ Coding/Build → Builder
  └─ Sonstiges → CEO selbst
```

---

## Error Codes

| Code | Name | Beschreibung |
|------|------|--------------|
| MCP001 | INVALID_SCHEMA | Schema Validation fehlgeschlagen |
| MCP002 | CYCLE_DETECTED | Cycle/Loop geblockt |
| MCP003 | DUPLICATE_BLOCKED | Duplikat erkannt |
| MCP004 | MAX_DEPTH_EXCEEDED | Maximale Tiefe überschritten |
| MCP005 | MAX_RETRIES_EXCEEDED | Retry-Limit erreicht |
| MCP006 | UNKNOWN_TOOL | Tool nicht gefunden |
| MCP007 | ROUTING_FAILED | Routing fehlgeschlagen |

---

*End of MCP Specification v1.0*
