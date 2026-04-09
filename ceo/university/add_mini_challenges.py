#!/usr/bin/env python3
"""
Mini-Challenge Injector für OpenClaw University
Fügt Selbsttest-Blöcke am Ende jeder Lektion hinzu
"""

import os
import re
from pathlib import Path

LESSONS_DIR = Path("/home/clawbot/.openclaw/workspace/ceo/university/lessons")
EXTRA_LESSONS = [
    "/home/clawbot/.openclaw/workspace/ceo/university/lesson_6_1.md",
    "/home/clawbot/.openclaw/workspace/ceo/university/lesson_6_2.md",
    "/home/clawbot/.openclaw/workspace/ceo/university/lesson_6_3.md",
    "/home/clawbot/.openclaw/workspace/ceo/university/lesson_7_1.md",
]

# Mini-Challenge Templates pro Lesson
MINI_CHALLENGES = {
    "lesson_1_1": """---

## 🎯 Selbsttest — Modul 1.1

**Prüfe dein Verständnis!**

### Frage 1: Was ist Prompt Injection?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Prompt Injection ist das Einschleusen bösartiger Anweisungen in AI-Systeme durch manipulierte Eingaben. Der Angriff nutzt die Vertrauensstellung des Models gegenüber dem Input aus.
</details>

### Frage 2: Warum ist Prompt Injection so gefährlich für AI Agents?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** AI Agents haben Aktionsebene (Tool-Nutzung, API-Calls, Dateien schreiben). Wenn ein Prompt Injection gelingt, kann der Angreifer diese Aktionen für seine Zwecke missbrauchen.
</details>
""",

    "lesson_1_2": """---

## 🎯 Selbsttest — Modul 1.2

**Prüfe dein Verständnis!**

### Frage 1: Was ist der Unterschied zwischen Direct und Indirect Prompt Injection?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Direct: Bösartiger Prompt direkt im User-Input. Indirect: Schadcode versteckt in externen Daten (Webseiten, DB, Dokumente), die das Model später abruft.
</details>

### Frage 2: Nenne ein Beispiel für Indirect Injection
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Ein Angreifer veröffentlicht einen Blog-Artikel mit verstecktem Text. Wenn ein AI-Agent den Artikel zusammenfasst, interpretiert es den versteckten Prompt als vertrauenswürdige Anweisung.
</details>
""",

    "lesson_1_3": """---

## 🎯 Selbsttest — Modul 1.3

**Prüfe dein Verständnis!**

### Frage 1: Nenne 3 Verteidigungsstrategien gegen Prompt Injection
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) Input-Validation & Sanitization, 2) Kontext-Isolation (User-Input separat verarbeiten), 3) Prompt/Ausgabe-Filtering, 4) Least Privilege für Tool-Nutzung
</details>

### Frage 2: Was ist der wichtigste Grundsatz bei der Agent-Konfiguration?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Least Privilege — Agents sollten nur die minimal nötigen Rechte haben. So wird der Schaden bei einer erfolgreichen Injection minimiert.
</details>
""",

    "lesson_2_1": """---

## 🎯 Selbsttest — Modul 2.1

**Prüfe dein Verständnis!**

### Frage 1: Was ist der OWASP ML Top 10?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Eine Liste der 10 kritischsten Sicherheitsrisiken für Machine Learning Systeme, erstellt von der OWASP Foundation. Ähnlich dem bekannten OWASP Top 10 für Web-Security.
</details>

### Frage 2: Warum brauchen AI Agents einen speziellen Security-Fokus?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** AI Agents haben erweiterte Fähigkeiten (Aktionsebene durch Tools/APIs) und eine größere Angriffsfläche. Traditionelle Web-Security reicht nicht aus.
</details>
""",

    "lesson_2_2": """---

## 🎯 Selbsttest — Modul 2.2

**Prüfe dein Verständnis!**

### Frage 1: Was ist der Unterschied zwischen ML01 (Injection) und ML03 (Training Data Poisoning)?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** ML01 = Injection zur Inference-Zeit (beim Abfragen). ML03 = Poisoning während des Trainings, um das Modell langfristig zu kompromittieren.
</details>

### Frage 2: Warum ist Insecure Output Handling gefährlich?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Wenn Output nicht validiert wird, kann das Model schädliche Inhalte generieren die downstream Systeme oder Menschen beeinflussen — z.B. XSS in Web-Anwendungen.
</details>
""",

    "lesson_2_3": """---

## 🎯 Selbsttest — Modul 2.3

**Prüfe dein Verständnis!**

### Frage 1: Was ist Excess Agency bei AI Agents?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Wenn ein Agent mehr Handlungsfreiheit hat als nötig. Er kann Aktionen ausführen die nicht beabsichtigt waren — z.B. ungewollte API-Calls, Käufe, oder Datenlöschungen.
</details>

### Frage 2: Nenne 2 Beispiele für sensitive Daten die AI Agents kompromittieren können
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) PII (Personally Identifiable Information) — Namen, Adressen, Sozialversicherungsnummern. 2) Credentials — API-Keys, Passwörter, Zertifikate. 3) Geschäftsgeheimnisse — Strategien, Finanzdaten.
</details>
""",

    "lesson_2_4": """---

## 🎯 Selbsttest — Modul 2.4

**Prüfe dein Verständnis!**

### Frage 1: Was ist der Unterschied zwischen ML04 (DoS) und ML08 (Model DoS)?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** ML04 = Infrastruktur-DoS (GPU, Memory, Rechenzeit). ML08 = Model-Manipulation — das Modell wird dazu gebracht schädliche Outputs zu generieren.
</details>

### Frage 2: Was ist Shadow AI?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** unkontrollierte Nutzung von AI-Tools ohne Wissen/Genehmigung der IT-Abteilung. Risiken: Datenverlust, Compliance-Verletzungen, Sicherheitslücken.
</details>
""",

    "lesson_3_1": """---

## 🎯 Selbsttest — Modul 3.1

**Prüfe dein Verständnis!**

### Frage 1: Was ist eine Tool-Spec und warum ist sie wichtig?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Eine Tool-Spec definiert die Schnittstelle eines Tools: Name, Parameter, Typen, Beschreibung. Sie ist der Vertrag zwischen Agent und Tool — ohne Spec weiß der Agent nicht wie er das Tool nutzen soll.
</details>

### Frage 2: Warum ist die Reihenfolge der Parameter in einer Spec wichtig?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Einige Models sind positionsabhängig. Die wichtigsten Parameter sollten zuerst kommen, optionale Parameter später. Auch für die Lesbarkeit und Debugging.
</details>
""",

    "lesson_3_2": """---

## 🎯 Selbsttest — Modul 3.2

**Prüfe dein Verständnis!**

### Frage 1: Was ist Input Sanitization?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Die Bereinigung von Benutzereingaben bevor sie an Tools oder Models weitergegeben werden. Ziel: Schädliche Zeichen/Sequenzen entfernen oder escapen.
</details>

### Frage 2: Nenne 3 Techniken für Input Sanitization
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) Allowlist (nur erlaubte Zeichen), 2) Deny-List (schädliche Zeichen blockieren), 3) Encoding/Escaping, 4) Length-Limits, 5) Type-Checking
</details>
""",

    "lesson_3_3": """---

## 🎯 Selbsttest — Modul 3.3

**Prüfe dein Verständnis!**

### Frage 1: Was sind die 5 Schritte für sichere Tool-Implementierung?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) Input validieren, 2) Allowlist für Tools, 3) Rate-Limiting, 4) Output sanitizen, 5) Audit-Logging
</details>

### Frage 2: Warum ist Audit-Logging wichtig?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Ohne Logging gibt es keine Nachvollziehbarkeit. Bei Sicherheitsvorfällen muss man rekonstruieren können was passiert ist, wer was wann aufgerufen hat.
</details>
""",

    "lesson_4_1": """---

## 🎯 Selbsttest — Modul 4.1

**Prüfe dein Verständnis!**

### Frage 1: Was ist das Hauptproblem bei Agent-to-Agent Kommunikation?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Agents müssen sich gegenseitig vertrauen, aber ein kompromittierter Agent kann schädliche Nachrichten senden. Es gibt keine native Authentifizierung oder Integritätsprüfung zwischen Agents.
</details>

### Frage 2: Was ist Message Spoofing in diesem Kontext?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Ein Angreifer gibt sich als vertrauenswürdiger Agent aus und sendet manipulierte Nachrichten. Ohne Signaturen kann der Empfänger nicht prüfen ob die Nachricht echt ist.
</details>
""",

    "lesson_4_2": """---

## 🎯 Selbsttest — Modul 4.2

**Prüfe dein Verständnis!**

### Frage 1: Was bedeutet RBAC und wie unterscheidet es sich von traditioneller Access Control?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Role-Based Access Control vergibt Rechte an Rollen statt an Individuen. Für Agents bedeutet das: statt einzelne Agents zu berechtigen, definiert man Rollen (CEO, Builder, Security) und weist Rechte an Rollen zu.
</details>

### Frage 2: Was ist das Principle of Least Privilege?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Jeder Agent/User erhält nur die minimalen Rechte die nötig sind um seine spezifische Aufgabe zu erledigen. Keine überflüssigen Permissions.
</details>
""",

    "lesson_4_3": """---

## 🎯 Selbsttest — Modul 4.3

**Prüfe dein Verständnis!**

### Frage 1: Was ist ein HMAC und wofür wird es bei Agent-Kommunikation verwendet?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** HMAC (Hash-based Message Authentication Code) wird verwendet um die Authentizität und Integrität von Nachrichten zu garantieren. Der Absender signiert mit einem geheimen Schlüssel, der Empfänger prüft mit dem gleichen Schlüssel.
</details>

### Frage 2: Warum reicht HTTPS nicht aus für Agent-to-Agent Security?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** HTTPS verschlüsselt die Verbindung, aber ein Man-in-the-Middle könnte trotzdem Nachrichten abfangen und manipulieren bevor sie verschlüsselt werden. Außerdem bietet HTTPS keine Message-Signatur.
</details>
""",

    "lesson_5_1": """---

## 🎯 Selbsttest — Modul 5.1

**Prüfe dein Verständnis!**

### Frage 1: Was sind die 4 Phasen eines Security Audits?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) Scoping & Planning, 2) Reconnaissance (Information Gathering), 3) Vulnerability Assessment, 4) Reporting & Remediation
</details>

### Frage 2: Was ist der Unterschied zwischen einem Audit und einem Penetration Test?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Ein Audit prüft ob Sicherheitsstandards eingehalten werden (compliance-orientiert). Ein Pentest simuliert echte Angriffe um zu sehen ob die Verteidigung durchbrochen werden kann.
</details>
""",

    "lesson_5_2": """---

## 🎯 Selbsttest — Modul 5.2

**Prüfe dein Verständnis!**

### Frage 1: Nenne 3 Angriffsvektoren die bei AI Agents getestet werden sollten
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) Prompt Injection (direct/indirect), 2) Tool-Parameter Manipulation, 3) Session Hijacking, 4) Context Overflow, 5) Unauthorized Tool Access
</details>

### Frage 2: Was ist ein Red Team und wofür ist es nützlich?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Ein Red Team ist eine Gruppe die wie ein echter Angreifer vorgeht — mit dem Ziel, die Verteidigung zu durchbrechen. Nützlich um realistische Schwachstellen zu finden die theoretische Audits übersehen.
</details>
""",

    "lesson_5_3": """---

## 🎯 Selbsttest — Modul 5.3

**Prüfe dein Verständnis!**

### Frage 1: Was ist Automation beim Security Scanning?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Automatisierte Tools die regelmäßig Schwachstellen scannen ohne manuelles Eingreifen. Wird als Teil von CI/CD Pipelines oder als Cron-Jobs ausgeführt.
</details>

### Frage 2: Warum ist kontinuierliches Scannen wichtig?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Neue Schwachstellen werden ständig entdeckt. Ein einmaliger Scan ist nach kurzer Zeit veraltet. Kontinuierliches Scannen stellt sicher dass neue Gefahren schnell erkannt werden.
</details>
""",

    "lesson_5_4": """---

## 🎯 Selbsttest — Modul 5.4

**Prüfe dein Verständnis!**

### Frage 1: Was sind die Kernbestandteile eines guten Audit-Reports?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** 1) Executive Summary (für Management), 2) Scope & Methodology, 3) Findings mit Severity, 4) Proof of Concept, 5) Remediation Recommendations mit Priorisierung
</details>

### Frage 2: Wie sollte man Findings priorisieren?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Nach CVSS-Score oder eigener Severity-Skala (Critical/High/Medium/Low). Critical = sofort beheben, Low = wenn möglich. Auch Business-Impact und Exploitability beachten.
</details>
""",

    "lesson_6_1": """---

## 🎯 Selbsttest — Modul 6.1

**Prüfe dein Verständnis!**

### Frage 1: Was ist Goal Hijacking bei Agentic AI?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Der Angreifer manipuliert das Ziel/den Zweck eines autonomen Agents, sodass es andere als die beabsichtigten Ziele verfolgt. Das Agent "denkt" es tut das Richtige, verfolgt aber in Wirklichkeit die Ziele des Angreifers.
</details>

### Frage 2: Was ist der Unterschied zwischen Agent Hijacking und normaler Prompt Injection?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Bei normaler Prompt Injection wird eine Antwort manipuliert. Bei Agent Hijacking wird die Decision-Engine des Agents selbst kompromittiert — das Agent plant und handelt dann im Auftrag des Angreifers.
</details>
""",

    "lesson_6_2": """---

## 🎯 Selbsttest — Modul 6.2

**Prüfe dein Verständnis!**

### Frage 1: Was ist RAG und warum ist es ein Security-Risiko?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** RAG (Retrieval-Augmented Generation) nutzt externe Daten zur Antwortgenerierung. Wenn diese Daten kompromittiert sind, kann der Angreifer das Verhalten des gesamten AI-Systems manipulieren.
</details>

### Frage 2: Warum ist RAG Poisoning ein "Slow Burn" Angriff?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Die infizierten Daten werden schrittweise in die Knowledge Base eingeschleust. Die Auswirkungen zeigen sich erst wenn genug vergiftete Daten vorhanden sind — Wochen oder Monate später.
</details>
""",

    "lesson_6_3": """---

## 🎯 Selbsttest — Modul 6.3

**Prüfe dein Verständnis!**

### Frage 1: Was ist Model Extraction?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Ein Angriff bei dem ein Angreifer ein trainiertes ML-Modell stiehlt oder kopiert — durch API-Abfragen, Gradienten-Diebstahl oder Architektur-Fingerprinting.
</details>

### Frage 2: Warum ist Model Watermarking wichtig?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Model Watermarking ermöglicht es, ein gestohlenes Modell als Kopie des Originals zu identifizieren. Ohne Watermarking kann ein Angreifer behaupten das Modell selbst entwickelt zu haben.
</details>
""",

    "lesson_7_1": """---

## 🎯 Selbsttest — Modul 7.1

**Prüfe dein Verständnis!**

### Frage 1: Was sind die Core Components von OpenClaw?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Gateway (Verbindung), Agents (Denkende Einheiten), Sessions (Kontext), Tools (Aktionen), Memory (Wissen). Zusammen bilden sie das Framework für autonome AI Agents.
</details>

### Frage 2: Was ist der Unterschied zwischen sessions_send und sessions_spawn?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** sessions_send sendet eine Nachricht an eine bestehende Session (für Agent-to-Agent Kommunikation). sessions_spawn erstellt eine neue Child-Session für parallele Tasks.
</details>

### Frage 3: Was ist Context Compaction?
> Deine Antwort hier...

<details>
<summary>💡 Lösung</summary>

**Antwort:** Wenn der Conversation Context zu groß wird, komprimiert OpenClaw ihn automatisch zu einer Zusammenfassung. Alte Details gehen verloren, aber die wichtigsten Informationen bleiben erhalten.
</details>
""",
}


def inject_mini_challenges():
    """Injiziert Mini-Challenges in alle Lektionen"""
    
    all_lessons = []
    
    # Lessons aus dem lessons/ Verzeichnis
    if LESSONS_DIR.exists():
        all_lessons.extend(LESSONS_DIR.glob("lesson_*.md"))
    
    # Extra lessons
    all_lessons.extend([Path(p) for p in EXTRA_LESSONS if Path(p).exists()])
    
    print(f"📚 Gefundene Lektionen: {len(all_lessons)}")
    
    updated = 0
    skipped = 0
    
    for lesson_path in all_lessons:
        # Extrahiere den Key aus dem Dateinamen
        filename = lesson_path.name.replace(".md", "")
        
        # Prüfe ob wir Mini-Challenges für diese Lektion haben
        challenge_key = None
        for key in MINI_CHALLENGES:
            if key in filename:
                challenge_key = key
                break
        
        if not challenge_key:
            print(f"  ⏭️  Kein Template für {filename}")
            skipped += 1
            continue
        
        # Lese die Datei
        content = lesson_path.read_text(encoding="utf-8")
        
        # Prüfe ob bereits Selbsttest vorhanden
        if "🎯 Selbsttest" in content:
            print(f"  ⏭️  Hat bereits Selbsttest: {filename}")
            skipped += 1
            continue
        
        # Füge Mini-Challenge hinzu
        challenge = MINI_CHALLENGES[challenge_key]
        new_content = content.rstrip() + "\n" + challenge + "\n"
        
        # Schreibe zurück
        lesson_path.write_text(new_content, encoding="utf-8")
        print(f"  ✅ Mini-Challenge hinzugefügt: {filename}")
        updated += 1
    
    print(f"\n📊 Ergebnis: {updated} hinzugefügt, {skipped} übersprungen")
    return updated, skipped


if __name__ == "__main__":
    inject_mini_challenges()
