# Example 1: Knowledge Graph (PARA Structure)

## Layer 1: Knowledge Graph mit automatischer Fakten-Extraktion

```
┌─────────────────────────────────────────────────────────────┐
│                  KNOWLEDGE GRAPH (PARA)                     │
├─────────────────────────────────────────────────────────────┤
│  Entities:                                                  │
│  ───────────────────────────────────────────────────────   │
│                                                             │
│  🟢 CRITICAL (Score 1.0)                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Master (Areas)                                       │   │
│  │ • "Ich heiße Nico" (confidence: 0.9)               │   │
│  │ • "will €100/Monat verdienen" (confidence: 0.9)    │   │
│  │ • "kommuniziert am liebsten auf Deutsch"           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  🟡 HIGH (Score 0.7-0.9)                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ POD-Business (Projects)                              │   │
│  │ • "Etsy + Printful Integration"                    │   │
│  │ • "Ziel: €100/Monat"                                │   │
│  │ • "Nischen: Gaming, Pet, Humor"                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  🔵 MEDIUM (Score 0.5-0.7)                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ AI-Trading (Areas)                                  │   │
│  │ • "Recherchiert Trading-Strategien"                │   │
│  │ • "Nutzt MiniMax + Gemini"                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ⚪ LOW/ARCHIVE (Score < 0.5)                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Old Ideas (Archives)                                │   │
│  │ • Alte, nicht mehr abgerufene Fakten                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Automatische Extraktion aus Nachricht:

```
User sagt: "Ich heiße Nico und will €100 pro Monat mit POD verdienen!"

↓ Automatisch extrahiert:

┌────────────────────────────────────────┐
│ category: preference                  │
│ content: "Ich heiße Nico"              │
│ confidence: 0.9                        │
│ priority: CRITICAL                     │
├────────────────────────────────────────┤
│ category: goal                         │
│ content: "€100 pro Monat mit POD"     │
│ confidence: 0.9                        │
│ priority: HIGH                         │
├────────────────────────────────────────┤
│ category: project                     │
│ content: "Print-on-Demand Business"   │
│ confidence: 0.8                        │
│ priority: HIGH                         │
└────────────────────────────────────────┘
```
