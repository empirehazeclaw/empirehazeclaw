# ENTITY TYPES ERWEITERUNG — Knowledge Graph

**Erstellt:** 2026-04-10
**Basierend auf:** knowledge-graph-skill research

---

## 🎯 ZIEL

Unsere KG Entity Types erweitern von aktuell ~10 auf 19 Types (wie knowledge-graph-skill).

---

## 📊 AKTUELLE ENTITY TYPES (falls vorhanden)

Typische aktuelle Types:
- human
- ai
- device
- project
- concept
- skill
- org
- service
- event
- place
- knowledge

---

## 🎯 ZIEL: 19 ENTITY TYPES

Basierend auf knowledge-graph-skill:

| # | Type | Beschreibung | Beispiel |
|---|------|-------------|---------|
| 1 | human | Personen | Nico, Partner |
| 2 | ai | AI Agents/Systeme | Sir HazeClaw, GPT |
| 3 | device | Physische Geräte | Server, Laptop |
| 4 | platform | Software-Plattformen | Telegram, Discord |
| 5 | project | Projekte | EmpireHazeClaw |
| 6 | decision | Wichtige Entscheidungen | "OpenRouter gewählt" |
| 7 | concept | Abstrakte Konzepte | Automation, Security |
| 8 | skill | Fähigkeiten/Tools | Scripting, Security Audit |
| 9 | network | Netzwerke/APIs | API Endpoints |
| 10 | credential | Secrets/API Keys | (sollte in Vault!) |
| 11 | org | Organisationen |缓冲区, GitHub |
| 12 | service | Dienste | OpenClaw Gateway |
| 13 | place | Orte | Server Standort |
| 14 | event | Ereignisse | "Gateway Down 2026-04-09" |
| 15 | media | Content/Medien | Tweets, Blog Posts |
| 16 | product | Produkte | SaaS Product |
| 17 | account | Accounts | Email, Social |
| 18 | routine | Routinen/Prozesse | Morning Routine |
| 19 | knowledge | Wissens-Artikel | Gelernte Konzepte |

---

## 🔍 FEHLENCE TYPES IDENTIFIZIERT

Basierend auf unserem System:

| Fehlender Type | Warum wichtig | Beispiel |
|----------------|--------------|---------|
| credential | Secrets sollten extra sein | API Keys |
| routine | Für wiederkehrende Prozesse | Morning Brief |
| account | Accounts sind wichtig | Email, Social |
| product | Für Business Stuff | Unser SaaS |

---

## 📝 IMPLEMENTIERUNG

### Wann neuen Entity Type verwenden:

```
NEW ENTITY:
- Ist es eine Person? → human
- Ist es ein AI Agent? → ai
- Ist es ein Device? → device
- Ist es ein Credential? → credential (in Vault!)
- Ist es eine Routine? → routine
- Ist es ein Account? → account
- Ist es ein Produkt? → product
```

---

## 🔄 MIGRATION

Wenn wir KG erweitern:

1. Prüfe alle existierenden entities
2. Markiere neue Types die fehlen
3. Update entity types wo nötig
4. Dokumentiere in KG schema

---

## 📋 RELATION TYPES (auch erweitern)

Aktuell:
- owns, uses, runs_on, runs, created
- related_to, part_of, instance_of
- decided, depends_on, connected
- manages, likes, dislikes
- located_in, knows, member_of, has

Neu hinzufügen:
| Relation | Verwendung |
|----------|-----------|
| follows | accounts, topics |
| scheduled_for | events, routines |
| has_access | accounts, credentials |

---

## 🎯 NÄCHSTE SCHRITTE

1. ⏳ Aktuelle KG Entity Types analysieren
2. ⏳ Fehlende Types identifizieren
3. ⏳ Neue Entities erstellen wo nötig
4. ⏳ KG Schema aktualisieren

---

*Erlernt aus: knowledge-graph-skill (ClawHub)*
