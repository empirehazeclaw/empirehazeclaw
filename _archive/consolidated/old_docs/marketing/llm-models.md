# 🤖 LLM Modelle - Analyse & Vergleich

## Verfügbare Modelle

### 🔥 High-Performance (Kostenlos/Günstig)

| Model | Alias | Context | Stärken | Schwächen | Best For |
|-------|-------|---------|---------|-----------|----------|
| **Llama 3.3 70B** | hunter-alpha | 128K | Sehr gutes Preis-Leistung, schnell, Open Source | Nicht ganz so gut bei komplexen Reasoning | Coding, Allgemein |
| **Gemini 2.0 Flash** | - | 1M | **Größter Context**, gratis, schnell | Weniger kreativ | Lange Dokumente, Recherche |
| **Llama 3.1 405B** | - | 128K | Leistungsstärkstes Open Source | Langsam, teurer | Komplexe Aufgaben |

### 💎 Premium (Genau)

| Model | Alias | Context | Stärken | Schwächen | Best For |
|-------|-------|---------|---------|-----------|----------|
| **Claude 3.5 Sonnet** | healer-alpha | 200K | Beste Qualität, Tool Use, Sicherheit | Teurer | Coding, Analysis, Safety |
| **GPT-4o** | - | 128K | Ausgewogen, gutes Ecosystem | Teuer, weniger Context | Allround |

### ⚡ Schnell & Billig

| Model | Context | Stärken | Schwächen | Best For |
|-------|---------|---------|-----------|----------|
| **MiniMax M2.5** | 200K | Sehr günstig (oft gratis), Reasoning | Weniger Tools | Bulk tasks |
| **MiniMax M2.1** | 200K | Am günstigsten | Schwächer bei komplexen Aufgaben | Simple tasks |

---

## 📊 Empfehlung nach Use-Case

| Use-Case | Empfehlenes Model | Warum |
|----------|-------------------|-------|
| **Coding** | hunter-alpha (Llama 3.3) | Schnell, günstig, gut bei Code |
| **Analyse/Research** | healer-alpha (Claude 3.5) | Beste Qualität, lange Context |
| **Lange Dokumente** | Gemini 2.0 Flash | 1M Context! |
| **Budget** | MiniMax M2.1 | Kostenlos (Portal) |
| **Allround** | GPT-4o | Ausgewogen |

---

## 💰 Kostenvergleich (pro 1M tokens)

| Model | Input | Output |
|-------|-------|--------|
| Gemini 2.0 Flash | $0.10 | $0.10 |
| Llama 3.3 70B | $0.10 | $0.10 |
| GPT-4o | $2.50 | $10.00 |
| Claude 3.5 Sonnet | $3.00 | $15.00 |
| MiniMax (Portal) | $0 | $0 |

---

## 🎯 Verfügbare Aliase in OpenClaw

- `hunter-alpha` → meta-llama/llama-3.3-70b-instruct
- `healer-alpha` → anthropic/claude-3.5-sonnet
- `minimax-m2.1` → MiniMax-M2.1
- `minimax-m2.5` → MiniMax-M2.5

---

*Erstellt: 2026-03-13*
