# Modul 6.3 — Lösungsschlüssel: Model Extraction

**Kurs:** OpenClaw University
**Modul:** 6.3 — Model Extraction
**Erstellt:** 2026-04-08

---

## TEIL A — Multiple Choice (40 Punkte)

---

## Frage 1 — Lösung

**Richtige Antwort: b**

**Erklärung:** Model Extraction ist ein Angriff bei dem ein Angreifer ein trainiertes Modell stiehlt oder kopiert — entweder durch API-Abfragen, Gradienten-Diebstahl oder Architektur-Fingerprinting.

---

## Frage 2 — Lösung

**Richtige Antwort: c**

**Erklärung:** Proprietäres IP (Trainingsdaten, Architektur) wird gestohlen. Konkurrenten erhalten unfairen Vorteil, da sie die Millionen-Investitionen in Training umgehen.

---

## Frage 3 — Lösung

**Richtige Antwort: b**

**Erklärung:** Training Data Extraction stiehlt Daten die das Modell während des Trainings "gemerkt" hat. Model Extraction stiehlt das Modell selbst — seine Gewichte, Architektur und Funktionalität.

---

## Frage 4 — Lösung

**Richtige Antwort: b**

**Erklärung:** API-basiertes Model Stealing nutzt die API mit vielen Queries um Responses zu sammeln. Mit genug Daten kann ein approximatives Modell trainiert werden — für nur API-Gebühren statt Millionen für Training.

---

## Frage 5 — Lösung

**Richtige Antwort: b**

**Erklärung:** Latency Fingerprinting — wie lange bestimmte Queries dauern — gibt Hinweise auf die Infrastruktur und Architektur des Modells (z.B. Modellgröße, GPU-Setup).

---

## Frage 6 — Lösung

**Richtige Antwort: b**

**Erklärung:** Model Watermarking ist eine Technik um ein Modell eindeutig zu markieren (z.B. durch versteckte Signaturen in Outputs). Dies ermöglicht es, ein gestohlenes Modell als Kopie des Originals zu identifizieren.

---

## Frage 7 — Lösung

**Richtige Antwort: b**

**Erklärung:** Output Perturbation fügt kontrolliertes Rauschen zu den Outputs hinzu. Dies zerstört die Nützlichkeit nicht komplett, erschwert aber die Rekonstruktion des exakten Modells für den Angreifer.

---

## Frage 8 — Lösung

**Richtige Antwort: c**

**Erklärung:** Query- und Rate-Limiting ist die erste Verteidigungslinie — sie verhindert dass ein Angreifer unbegrenzt Daten sammeln kann. Die anderen Maßnahmen sind zusätzliche Schichten.

---

## Frage 9 — Lösung

**Richtige Antwort: b**

**Erklärung:** Query Diversity misst wie vielfältig die Fragen eines Clients sind. Geringe Diversity (immer ähnliche Queries) deutet auf einen Angreifer hin, der systematisch Daten sammelt.

---

## Frage 10 — Lösung

**Richtige Antwort: c**

**Erklärung:** Legal Protection (Lizensierung, AGB, Verträge) ermöglicht rechtliche Schritte gegen Diechtebstahl — auch wenn technische Maßnahmen umgangen wurden.

---

## TEIL B — True/False (15 Punkte)

---

## Frage 11 — Lösung

**Richtige Antwort: Falsch**

**Erklärung:** Model Extraction ist KEINESFALLS harmlos. Selbst wenn das Original noch funktioniert, entsteht massive Schädigung durch: IP-Diebstahl, Wettbewerbsnachteil, finanzielle Verluste.

---

## Frage 12 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** Bei Gradient-Based Extraction hat ein Angreifer der Zugang zu den Gradienten (z.B. bei Federated Learning) genug Information um die Gewichte direkt zu rekonstruieren — große Gradienten = wichtige Gewichte, kleine = weniger wichtig.

---

## Frage 13 — Lösung

**Richtige Antwort: Falsch**

**Erklärung:** Output Perturbation fügt nur minimales, kontrolliertes Rauschen hinzu. Die Nützlichkeit des Modells bleibt erhalten, aber die exakte Rekonstruktion wird erschwert.

---

## Frage 14 — Lösung

**Richtige Antwort: Wahr**

**Erklärung:** Model Watermarking bettet kryptografische Signaturen in alle Outputs ein. Wenn ein gestohlenes Modell gefunden wird, kann man durch Analyse der Outputs nachweisen dass es eine Kopie ist.

---

## Frage 15 — Lösung

**Richtige Antwort: Falsch**

**Erklärung:** Rate-Limiting allein reicht NICHT aus. Ein Angreifer kann:
- Viele verschiedene Clients nutzen
- Langsam aber systematisch sammeln
- Social Engineering nutzen

Defense-in-Depth mit mehreren Schichten ist nötig.

---

## TEIL C — Praxisfrage (5 Punkte)

---

## Frage 16 — Lösung

**Antwort:**

API-basiertes Model Stealing ist für Angreifer attraktiv wegen der **Kosten-Nutzen-Rechnung**:

**Kosten für Angreifer:**
- Nur API-Gebühren (z.B. $0.01/Query)
- Für 1 Million Queries: ~$10.000

**Kosten für Original:**
- Millionen in Training investiert
- Jahrelange Forschung & Entwicklung

**Ergebnis für Angreifer:**
- Ein Modell mit ~85-90% der Fähigkeiten
- Für <1% der Original-Kosten
- Sofort einsatzbereit

**Anreiz:** Maximale Rendite auf minimale Investition.

---

**Ende des Lösungsschlüssels**
