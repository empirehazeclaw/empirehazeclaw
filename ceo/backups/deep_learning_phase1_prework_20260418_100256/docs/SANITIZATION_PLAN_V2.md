# 🧹 Memory Sanitization — MASTER PLAN v2

## Basierend auf Research (2024-2025 Best Practices)

### Quellen:
- 📄 "The Empirical Impact of Data Sanitization on Language Models" (Amazon/AWS, Arxiv 2024)
- 🔒 AWS Blog: Context-aware PII detection mit Amazon Comprehend
- 🛡️ Reddit r/LocalLLaMA: Training data privacy
- 📊 Tonic.ai, RedactChat: Production anonymization tools

---

## 🔬 Research Findings

### 1. Problem mit naive Tokenization

> "Replacing diverse PII with generic tokens, for instance replacing two different names with the same `<NAME>` token introduces ambiguity, making it harder for the model to differentiate between unique entities."
> — Amazon Paper

**Lösung:** Statt `<NAME>` → `<PERSON_1>`, `<PERSON_2>` für konsistente mapping

### 2. Context-Aware Detection

> "Goes beyond surface-level detection with context-aware signals to flag when PII is implied but not explicitly stated"
> — Protecto AI NER comparison

**Lösung:** Nicht nur Regex, sondern auch NLP-ähnliche Kontext-Erkennung

### 3. Hybrid Approach (Rule-based + ML)

> "Data sanitization is generally achieved through replacing PII with non-sensitive tokens. Sanitization techniques typically use sequence labeling approaches, such as named entity recognition (NER) algorithms"
> — Arxiv Paper

**Lösung:** Regex + Pattern-Matching + Whitelist + Review

### 4. Reversibility für Audit

> "Whitelist specific terms" / "User review and control"
> — RedactChat

**Lösung:** Mapping-Datei für Restore + Whitelist-Option

---

## 🎯 SANITIZATION LEVELS

| Level | Methode | Datenschutz | Utility | Complexity |
|-------|---------|-------------|---------|-----------|
| **L1** | Basic Regex | 🟡 Mittel | 🟢 Hoch | 🟢 Simpel |
| **L2** | Context-Aware + Consistent | 🟢 Hoch | 🟢 Hoch | 🟡 Mittel |
| **L3** | LLM-Assisted + Differential Privacy | 🟢 Max | 🟡 Mittel | 🔴 Komplex |

---

## 📋 SENSITIVITY CATEGORIES

### 🔴 KRITISCH (Never leak, always sanitize)

| Typ | Regex Pattern | Token |
|-----|---------------|-------|
| API Keys | `sk-[a-zA-Z0-9]{20,}` | `{{API_KEY}}` |
| Bot Tokens | `\d{8,10}:[a-zA-Z0-9_-]{35}` | `{{BOT_TOKEN}}` |
| JWT Tokens | `eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+` | `{{JWT}}` |
| AWS Keys | `AKIA[0-9A-Z]{16}` | `{{AWS_KEY}}` |
| Database URLs | `(mongodb\|postgres)://[^\s]+` | `{{DB_URL}}` |
| Private Keys | `-----BEGIN [A-Z]+ PRIVATE KEY-----` | `{{PRIVATE_KEY}}` |

### 🟠 HOCH (Leak = Privacy Risk)

| Typ | Regex Pattern | Token |
|-----|---------------|-------|
| Emails | `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` | `{{EMAIL}}` |
| Telefon | `(\+49[\s-]?)?[0-9]{10,14}` | `{{PHONE}}` |
| Namen | Nico, Sir HazeClaw, etc. | `{{PERSON_1}}`, `{{PERSON_2}}` |
| Telegram IDs | `(?<![\d])[1-9]\d{8,10}(?![\d])` | `{{USER_ID}}` |
| Addresses | [Address patterns] | `{{ADDRESS}}` |

### 🟡 MITTEL (Identifying but less critical)

| Typ | Regex Pattern | Token |
|-----|---------------|-------|
| Domains | `empirehazeclaw\.(com\|de\|store)` | `{{DOMAIN}}` |
| Workspace Paths | `/home/[a-z]+/` | `{{WORKSPACE}}` |
| Timestamps | Unix timestamps | ⏰ BEHALTEN |
| Dates | 2026-04-14 | 📅 BEHALTEN |

### 🟢 LOW (Context, not identifying)

| Typ | Behandlung |
|-----|-----------|
| Skill-Namen | Optional anonymisieren |
| Script-Pfade | Generalisieren |
| Cron-Namen | Optional |

---

## 🔧 TECHNICAL APPROACH

### Phase 1: Pattern Discovery
```
1. Scanne alle Dateien
2. Finde alle sensiblen Patterns
3. Kategorisiere nach Sensitivity
4. Zeige Statistik
```

### Phase 2: Consistent Token Mapping
```
1. Erstelle konsistente Mapping-Tabelle
2. Gleicher Name/Value → gleicher Token
3. Preserve_count für statistische Analyse
4. Export Mapping als JSON
```

### Phase 3: Context-Aware Replacement
```
1. Regex- matching
2. Word-boundary awareness (keine timestamps)
3. Whitelist- checking
4. Context-validation
```

### Phase 4: Verification
```
1. Keine API Keys mehr?
2. Keine Emails?
3. Keine persönlichen Namen?
4. Utility erhalten? (Lesbarkeit)
```

### Phase 5: Export
```
1. JSON Export für Training
2. Markdown Export für Review
3. Diff-View für Änderungen
```

---

## 📊 FEATURES (vs. v1)

| Feature | v1 | v2 (Ziel) |
|---------|----|----|
| Regex Replacement | ✅ | ✅ |
| Consistent Token Mapping | ❌ | ✅ |
| Phone Number Fix | ❌ | ✅ |
| Context-Aware | ❌ | ✅ |
| Whitelist | ❌ | ✅ |
| Dry-Run | ✅ | ✅ |
| Restore | ❌ | ✅ |
| Verification | ❌ | ✅ |
| Differential Privacy | ❌ | 🔜 |
| LLM-Assisted | ❌ | 🔜 |
| JSON Export | ❌ | ✅ |
| HTML Diff View | ❌ | ✅ |

---

## 🚀 IMPLEMENTATION PRIORITIES

### Must-Have (v2 final)
- [x] Fix phone number pattern (timestamps bug)
- [x] Consistent token mapping (PERSON_1, PERSON_2)
- [x] Whitelist support
- [x] Restore from mapping
- [x] Verification step

### Should-Have (v3)
- [ ] Differential privacy noise option
- [ ] LLM-assisted context detection
- [ ] HTML diff report
- [ ] Incremental sanitization

### Nice-to-Have (future)
- [ ] NER-based detection (spaCy)
- [ ] Training data format export (LLama, Mistral)
- [ ] Privacy score calculation

---

## 📁 OUTPUT STRUCTURE

```
sanitized_memory/
├── _config.json          # Sanitization config
├── _mapping.json         # Original → Token mapping
├── _whitelist.json       # Whitelisted terms
├── _audit.json          # Audit trail
│
├── level1/              # L1: Basic sanitization
│   ├── facts.md
│   ├── patterns.md
│   └── ...
│
├── level2/              # L2: Full anonymization
│   ├── facts.md
│   ├── patterns.md
│   └── ...
│
├── level3/              # L3: Differential privacy
│   └── ...
│
└── exports/
    ├── training.json    # Für Model Training
    ├── review.md        # Human-readable summary
    └── diff.html        # Visual diff
```

---

## ✅ VERIFICATION CHECKLIST

Pre-Sanitize:
- [ ] Backup erstellt
- [ ] Whitelist definiert
- [ ] Dry-run durchgeführt
- [ ] Änderungen reviewed

Post-Sanitize:
- [ ] Keine API Keys in Output
- [ ] Keine Emails in Output
- [ ] Keine Telefonnummern in Output
- [ ] Keine persönlichen Namen (oder konsistent ersetzt)
- [ ] Timestamps erhalten
- [ ] Workflows/Logik intakt
- [ ] Mapping vollständig

---

## 🎓 LESSONS FROM RESEARCH

1. **Konsistenz ist key** — Gleiche Entität = Gleicher Token
2. **Context matters** — Manche PII ist "task-critical" und sollte evtl. bleiben
3. **Reversibilität** — Mapping für Audit und Restore
4. **Verification** — Automatische checks nach sanitize
5. **Balance** — Zu viel anonymization = weniger useful für training
