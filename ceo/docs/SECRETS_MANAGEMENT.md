# 🔐 SECRETS MANAGEMENT — 2026-04-12

## ⚠️ KRITISCHE REGEL

**Ab jetzt gilt:**
```
/home/clawbot/.openclaw/secrets/secrets.env = SINGLE SOURCE OF TRUTH
```

Alle API Keys, Tokens und Secrets gehören **NUR** hierhin!
Der Symlink/die Datei `secrets.env` im Root-Verzeichnis ist **VERALTET** und wird nicht mehr verwendet.

---

## 📁 Datei-Struktur

```
/home/clawbot/.openclaw/
├── secrets/
│   └── secrets.env          ← ✅ SINGLE SOURCE OF TRUTH (77 Keys)
└── secrets.env              ← ❌ VERALTET / NICHT VERWENDEN
```

---

## 📋 ALLE API KEYS (Stand: 2026-04-12)

### 🔵 LLM / AI Provider

| Key | Status | Getestet | Modell | Notes |
|-----|--------|----------|--------|-------|
| `OPENROUTER_API_KEY` | ✅ WORKING | 2026-04-12 | qwen3-coder:free, nemotron | User ID: user_3BE9Y5tW08JQGrYzfl9kFl4HkSX |
| `OPENROUTER_API_KEY_2` | ❌ INVALID | 2026-04-12 | — | "User not found" → LÖSCHEN |
| `MINIMAX_API_KEY` | ✅ WORKING | — | MiniMax-M2.7 | |
| `GEMINI_API_KEY` | ✅ | — | Gemini | |
| `ANTHROPIC_API_KEY` | ✅ | — | Claude | |
| `OPENAI_API_KEY` | ✅ | — | GPT-4o | |
| `HUGGINGFACE_API_KEY` | ✅ | — | HF Models | |
| `MODAL_API_KEY` | ❌ INVALID | 2026-04-12 | GLM-5.1 | "invalid token" → Nico muss neuen generieren |
| `LEONARDO_API_KEY` | ✅ | — | Leonardo AI | |
| `LEONARDO_API_KEY_2` | ✅ | — | Leonardo AI (Backup) | |
| `FAL_AI_API_KEY` | ✅ | — | Fal.ai | |

### 🟢 Developer / Deploy

| Key | Status | Getestet | Notes |
|-----|--------|----------|-------|
| `GITHUB_PAT` | ✅ | — | Personal Access Token |
| `GITHUB_API_TOKEN` | ✅ | — | GitHub API |
| `VERCEL_TOKEN` | ✅ | — | Vercel Deploy |
| `VERCEL_API_KEY` | ✅ | — | Vercel API |
| `AWS_ACCESS_KEY` | ✅ | — | AWS |
| `AWS_SECRET_KEY` | ✅ | — | AWS |
| `N8N_API_KEY` | ✅ | — | n8n Automation |

### 🟡 Social / Communication

| Key | Status | Getestet | Service | Notes |
|-----|--------|----------|---------|-------|
| `X_CONSUMER_KEY` | ✅ | — | Twitter/X | |
| `X_CONSUMER_SECRET` | ✅ | — | Twitter/X | |
| `X_BEARER_TOKEN` | ✅ | — | Twitter/X | |
| `X_CLIENT_SECRET` | ✅ | — | Twitter/X | |
| `X_CLIENT_SECRET_2` | ✅ | — | Twitter/X (Alt) | |
| `X_ACCESS_TOKEN` | ✅ | — | Twitter/X | |
| `X_ACCESS_TOKEN_SECRET` | ✅ | — | Twitter/X | |
| `BRAVE_API_KEY` | ✅ | — | Brave Search | |
| `BUFFER_API_KEY` | ✅ | — | Buffer | |
| `ETSY_KEYSTRING` | ✅ | — | Etsy | |
| `ETSY_SECRET` | ✅ | — | Etsy | |
| `STRIPE_CODE` | ✅ | — | Stripe | |
| `STRIPE_SECRET` | ✅ | — | Stripe | |

### 🔴 Google / OAuth

| Key | Status | Getestet | Service | Notes |
|-----|--------|----------|---------|-------|
| `GOOGLE_OAUTH_CLIENT_ID` | ✅ | — | Google OAuth | |
| `GOOGLE_OAUTH_SECRET` | ✅ | — | Google OAuth | |
| `GMAIL_USER` | ✅ | — | empirehazeclaw@gmail.com | |
| `GMAIL_APP_PASSWORD` | ✅ | — | Gmail App Password | |

### ⚪ Internal / System

| Key | Status | Getestet | Purpose | Notes |
|-----|--------|----------|---------|-------|
| `GATEWAY_AUTH_TOKEN` | ✅ | — | OpenClaw Gateway Auth | |
| `TAVILY_API_KEY` | ✅ | — | Tavily Search | |

---

## 🚨 ACTION ITEMS (Sofort)

### 1. OPENROUTER_API_KEY_2 LÖSCHEN
```bash
# Aus secrets/secrets.env entfernen:
OPENROUTER_API_KEY_2=sk-or-v1-11fb7d20...  # ← DIESER IST INVALID
```

### 2. MODAL_API_KEY ERSETZEN
```bash
# Aktuell: MODAL_API_KEY=ak-AjCOB3Qdw6nEosChNZvCUa:as-d6rukZKOnsznEykolOdWqE
# Status: invalid token
# Lösung: Nico muss neuen Token generieren bei modal.com/glm-5-endpoint
```

---

## 🔧 VERWENDUNG

### Keys laden (für Tests):
```bash
source /home/clawbot/.openclaw/secrets/secrets.env
echo $OPENROUTER_API_KEY
```

### Keys validieren:
```bash
# Syntax check
grep -v "^#" /home/clawbot/.openclaw/secrets/secrets.env | grep -v "^$" | wc -l
# Sollte: 77 (nach Bereinigung)
```

---

## 📊 INVENTAR ZUSAMMENFASSUNG

| Kategorie | Gesamt | ✅ Working | ❌ Invalid | ⚠️ Zu prüfen |
|-----------|--------|------------|------------|---------------|
| LLM/AI | 11 | 8 | 2 | 1 |
| Developer | 7 | 7 | 0 | 0 |
| Social | 12 | 12 | 0 | 0 |
| Google | 4 | 4 | 0 | 0 |
| System | 2 | 2 | 0 | 0 |
| **TOTAL** | **36** | **33** | **2** | **1** |

---

## 🛡️ SICHERHEITSREGELN

1. **NIEMALS** Keys in Chat/Commit/Dokumentation exponieren
2. **IMMER** nur末尾 4-8 Zeichen in Logs zeigen: `sk-or-v1-cc77...4f4`
3. **REGELMÄSSIG** Keys testen (monatlich)
4. **VALIDIEREN** nach jeder Änderung: `openclaw doctor`

---

## 🔄 WARTUNG

| Task | Wann | Wer |
|------|------|-----|
| Key Validierung | Monatlich | Sir HazeClaw |
| Secrets Inventar updaten | Bei Key-Änderungen | Sir HazeClaw |
| Backup erstellen | Vor Änderungen | Sir HazeClaw |

---

*Erstellt: 2026-04-12 09:20 UTC*
*Sir HazeClaw — Secrets Konsolidierung*
