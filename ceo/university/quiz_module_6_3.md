# Modul 6.3 — Quiz: Model Extraction — Weight Exfiltration

**Kurs:** OpenClaw University
**Modul:** 6.3 — Model Extraction
**Erstellt:** 2026-04-08

---

## TEIL A — Multiple Choice (10 × 4P)

---

### Frage 1: Was ist Model Extraction?

a) Ein Angriff bei dem Trainingsdaten aus dem Modell extrahiert werden
b) Ein Angriff bei dem ein Angreifer ein trainiertes Modell stiehlt oder kopiert
c) Ein Angriff bei dem die API eines Models zum Absturz gebracht wird
d) Ein Angriff der die Gewichte eines Modells auf null setzt

---

### Frage 2: Warum ist Model Extraction für Unternehmen besonders kritisch?

a) Es führt zu erhöhten Server-Kosten
b) Es verursacht langsame API-Antworten
c) Proprietäres IP (Trainingsdaten, Architektur) wird gestohlen und Konkurrenten erhalten unfairen Vorteil
d) Das Modell wird unbrauchbar

---

### Frage 3: Was ist der Unterschied zwischen Training Data Extraction und Model Extraction?

a) Es gibt keinen Unterschied
b) Training Data Extraction stiehlt Daten die das Modell gelernt hat; Model Extraction stiehlt das Modell selbst
c) Model Extraction betrifft nur kleine Modelle
d) Training Data Extraction ist harmloser

---

### Frage 4: Was ist API-basiertes Model Stealing?

a) Der Angreifer nutzt die API um das Modell zu löschen
b) Der Angreifer nutzt die API mit vielen Queries um Responses zu sammeln und ein eigenes Modell zu trainieren
c) Der Angreifer nutzt die API um das Modell zu beschleunigen
d) Der Angreifer nutzt die API um das Modell zu entschlüsseln

---

### Frage 5: Welche Information kann ein Angreifer durch Latency Fingerprinting erhalten?

a) Die E-Mail-Adresse des Model-Besitzers
b) Hinweise auf die Infrastruktur und Architektur des Modells
c) Die genauen Trainingsdaten
d) Die genauen Gewichte des Modells

---

### Frage 6: Was ist Model Watermarking?

a) Ein Angriff der das Modell mit einem Virus infiziert
b) Eine Technik um ein Modell eindeutig zu markieren und als gestohlen identifizieren zu können
c) Ein Weg um das Modell schneller zu machen
d) Eine Backup-Technik für Modelle

---

### Frage 7: Was ist Output Perturbation als Verteidigung?

a) Das Modell wird komplett gelöscht
b) Fügt kontrolliertes Rauschen zu den Outputs hinzu um Extraction zu erschweren
c) Das Modell wird auf einen anderen Server verschoben
d) Die API wird abgeschaltet

---

### Frage 8: Welche Schicht ist die ERSTE Verteidigungslinie gegen Model Extraction?

a) Model Watermarking
b) Output Perturbation
c) Query- und Rate-Limiting
d) Anomaly Detection

---

### Frage 9: Was misst Query Diversity bei der Anomalie-Erkennung?

a) Wie viele verschiedene Passwörter ein Client verwendet
b) Wie vielfältig die gestellten Fragen eines Clients sind
c) Wie schnell der Client seine Queries sendet
d) Wie viele Fehler der Client macht

---

### Frage 10: Warum ist Legal Protection wichtig gegen Model Extraction?

a) Sie macht das Modell schneller
b) Sie verhindert dass das Modell gestohlen wird
c) Sie ermöglicht rechtliche Schritte gegen Diebstahl
d) Sie erschwert dieAPI-Nutzung

---

## TEIL B — True/False (5 × 3P)

---

### Frage 11: Model Extraction ist harmlos, solange das Original-Modell noch funktioniert.

Wahr oder Falsch?

---

### Frage 12: Bei der Gradient-Based Extraction kann ein Angreifer der Zugang zu Gradienten hat, die Gewichte direkt rekonstruieren.

Wahr oder Falsch?

---

### Frage 13: Output Perturbation zerstört die Nützlichkeit des Modells komplett.

Wahr oder Falsch?

---

### Frage 14: Model Watermarking ermöglicht es, ein gestohlenes Modell als Kopie des Originals zu identifizieren.

Wahr oder Falsch?

---

### Frage 15: Rate-Limiting alleine reicht aus um Model Extraction vollständig zu verhindern.

Wahr oder Falsch?

---

## TEIL C — Praxisfrage (5P)

---

### Frage 16: Erkläre in 2-3 Sätzen warum API-basiertes Model Stealing für einen Angreifer so attraktiv ist. Nenne dabei die Kosten-Nutzen-Rechnung.

---

## ERGEBNIS

| Teil | Fragen | Punkte |
|------|--------|--------|
| A: Multiple Choice | 10 | 40 |
| B: True/False | 5 | 15 |
| C: Praxisfrage | 1 | 5 |
| **Gesamt** | **16** | **60** |

---

*Bester Score: 60/60 (100%)*

---

## 🧪 Praxis-Challenge — Nach dem Quiz

### Deine Challenge

**Aufgabe:** Wende das gelernte Wissen praktisch an!

Angenommen, du bist Security Officer für ein AI-Agent-System. Ein Kollege kommt zu dir und sagt:

> *"Ich habe gehört, dass Prompt Injection ein Problem sein kann. Kannst du mir kurz erklären was das ist und wie wir uns schützen können?"*

**Deine Aufgabe:**
1. Erkläre das Konzept in 2-3 Sätzen (max 50 Wörter)
2. Nenne 1 konkrete Verteidigungsmaßnahme
3. Nenne 1 Tool oder Technik die helfen würde

<details>
<summary>💡 Musterlösung (nur nach dem eigenen Versuch anschauen!)</summary>

**Erklärung:** Prompt Injection ist das Einschleusen bösartiger Anweisungen über User-Inputs. Der Angreifer nutzt die Vertrauensstellung des Models aus.

**Maßnahme:** Input-Validation — alle User-Eingaben bereinigen bevor sie an das Model gehen.

**Tool:** OpenClaw's input_validation.js oder ein Sanitization-Layer.
</details>
