# API Keys Inventory — 2026-04-12

## 🎯 Zusammenfassung

| Anbieter | Key | Status | Modelle |
|----------|-----|--------|---------|
| **OpenRouter** | `OPENROUTER_API_KEY` | ✅ FUNKTIONIERT | qwen3-coder:free, nemotron, gemma |
| **OpenRouter** | `OPENROUTER_API_KEY_2` | ❌ Ungültig | — |
| MiniMax | `MINIMAX_API_KEY` | ✅ Läuft | MiniMax-M2.7 |
| Google | `GEMINI_API_KEY` | ✅ | Gemini |
| Anthropic | `ANTHROPIC_API_KEY` | ✅ | Claude |
| OpenAI | `OPENAI_API_KEY` | ✅ | GPT-4o |
| HuggingFace | `HUGGINGFACE_API_KEY` | ✅ | HF Models |
| Modal | `MODAL_API_KEY` | ❌ Token ungültig | GLM-5.1 |

---

## 🔑 OpenRouter Keys

### Key 1 — AKTIV ✅
```
Location: /home/clawbot/.openclaw/secrets/secrets.env
Env Var:  OPENROUTER_API_KEY
Value:    sk-or-v1-cc77...4f4
User ID:  user_3BE9Y5tW08JQGrYzfl9kFl4HkSX
Status:   ✅ FUNKTIONIERT
Test:     nvidia/nemotron-3-super-120b-a12b:free — Response: WORKS
Rate Limit: qwen3-coder:free und gemma:free sind rate-limited
```

### Key 2 — INAKTIV ❌
```
Location: /home/clawbot/.openclaw/secrets/secrets.env
Env Var:  OPENROUTER_API_KEY_2
Value:    sk-or-v1-11fb...5f5ea
Status:   ❌ "User not found" — Key ungültig oder gelöscht
```

---

## 📁 Key Speicherorte

| Datei | Inhalt |
|-------|--------|
| `/home/clawbot/.openclaw/secrets/secrets.env` | **HAUPTQUELLE** — Alle Keys |
| `/home/clawbot/.openclaw/secrets.env` | Kopie (nur aktive Keys) |

---

## 🚀 OpenRouter Free Modelle (Verfügbar)

| Modell | Context | Status |
|--------|---------|--------|
| `qwen/qwen3-coder:free` | 262k | ⚠️ Rate-limited |
| `google/gemma-4-31b-it:free` | 262k | ⚠️ Rate-limited |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262k | ✅ **FUNKTIONIERT** |
| `minimax/minimax-m2.5:free` | 196k | ✅ |
| `liquid/lfm-2.5-1.2b-thinking:free` | 32k | ✅ |
| `openai/gpt-oss-120b:free` | 131k | ✅ |

---

## ⚠️ Probleme

### Modal Token Ungültig
```
MODAL_API_KEY=ak-AjCOB3Qdw6nEosChNZvCUa:as-d6rukZKOnsznEykolOdWqE
Error: invalid token
Lösung: Nico muss neuen Token generieren bei modal.com/glm-5-endpoint
```

### OpenRouter Key 2 Ungültig
```
OPENROUTER_API_KEY_2=sk-or-v1-11fb......
Error: User not found
Lösung: Aus secrets.env entfernen oder neuen Key generieren
```

---

## ✅ Nächste Schritte

1. [ ] Modal Token erneuern (Nico)
2. [ ] OpenRouter Key 2 aus Konfiguration entfernen (wenn nicht mehr gebraucht)
3. [ ] Nemotron als Fallback Modell testen

---

*Erstellt: 2026-04-12 09:15 UTC*
*Sir HazeClaw — API Key Dokumentation*
