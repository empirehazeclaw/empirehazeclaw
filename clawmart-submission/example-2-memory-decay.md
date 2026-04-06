# Example 2: Memory Decay System

## Wie Memory Decay funktioniert

Das Memory System nutzt **automatischen Verfall** um sicherzustellen, dass alte, irrelevante Fakten nicht das Gedächtnis überladen.

### Decay Formel

```
Score(t) = Score(0) × 0.9^(days_since_creation / 7)

Wöchentlicher Verfall: 9%
Score wird bei jedem Zugriff auf 1.0 zurückgesetzt
Score < 0.3 → Auto-Archive
```

---

## Visualisierung: Fakten-Verlauf

```
Neue Info hinzugefügt:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tag 0    ████████████████████████████████████████ 100% (1.0)
         "Neue Fakten hinzugefügt"

Tag 7    ██████████████████████████████████░░░░░░  91% (0.91)
         "Eine Woche alt"

Tag 14   █████████████████████████████░░░░░░░░░  83% (0.83)
         "Zwei Wochen alt"

Tag 30   ████████████████████░░░░░░░░░░░░░░░░░░  69% (0.69)
         "Ein Monat alt - wird selten abgerufen"

Tag 60   ██████████████░░░░░░░░░░░░░░░░░░░░░░░  48% (0.48)
         "Zwei Monate - MEDIUM Priority"

Tag 90   █████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  30% (0.30)
         "Kurz vor Archive - WICHTIG: Zugriff!"

        ↓ (Zugriff!) ↓
        
Tag 90+  ████████████████████████████████████████ 100% (1.0)
         "Zurückgesetzt durch Zugriff!"
```

---

## Priority Thresholds

```
┌─────────────────────────────────────────────────────────────┐
│  PRIORITY LEVELS                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CRITICAL  │ ████████████████████████████ │ Score ≥ 0.9   │
│             │ Häufig genutzt / Persönlich  │                │
│  ─────────────────────────────────────────────────────────  │
│  HIGH      │ █████████████████████░░░░░░░ │ Score ≥ 0.7   │
│             │ Wichtig für Projekte          │                │
│  ─────────────────────────────────────────────────────────  │
│  MEDIUM    │ █████████████████░░░░░░░░░░░ │ Score ≥ 0.5   │
│             │ Nützlicher Kontext             │                │
│  ─────────────────────────────────────────────────────────  │
│  LOW       │ ████████████░░░░░░░░░░░░░░░░░ │ Score ≥ 0.3   │
│             │ Referenz-Material              │                │
│  ─────────────────────────────────────────────────────────  │
│  ARCHIVE   │ ████████░░░░░░░░░░░░░░░░░░░░░ │ Score < 0.3   │
│             │ Wird selten abgerufen          │                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Beispiel: Auto-Promotion durch Zugriff

```
┌─────────────────────────────────────────────────────────────┐
│ BEFORE: Fakten-Änderung durch Zugriff                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Entity: "Python Script" (erstellt vor 60 Tagen)           │
│  ├── Initial Score: 1.0                                    │
│  ├── Nach 60 Tagen: 0.48 (LOW)                            │
│  └── Zugriff: 0x (nicht genutzt)                          │
│                                                             │
│  ───────────────────────────────────────────────────────   │
│                                                             │
│  Entity: "Master Name" (erstellt vor 60 Tagen)            │
│  ├── Initial Score: 1.0                                    │
│  ├── Nach 60 Tagen: 0.48 (LOW)                            │
│  └── Zugriff: 20x (jeden Tag!)                            │
│      ├── Score wird auf 1.0 zurückgesetzt                 │
│      ├── access_count: 20                                 │
│      └── Priority: CRITICAL (Auto-Promotion!)             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Warum Decay wichtig ist

| Ohne Decay | Mit Decay |
|------------|-----------|
| Alte, falsche Info wird immer noch abgerufen | Alte Info wird automatisch aussortiert |
| Gedächtnis wird mit irrelevanten Daten überladen | Nur relevante Fakten bleiben aktiv |
| Keine Priorisierung möglich | Wichtiges steigt automatisch auf |
| Qualität verschlechtert sich | Qualität bleibt hoch |
