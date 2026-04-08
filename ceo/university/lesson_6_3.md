# Lektion 6.3: Model Extraction — Weight Exfiltration

## Lernziele

- Verstehen was Model Extraction ist und warum es kritisch ist
- Die verschiedenen Angriffsmethoden kennen
- Die Angriffsoberfläche identifizieren
- Verteidigungsstrategien implementieren
- Realistische Szenarien verstehen und analysieren

---

## 1. Was ist Model Extraction?

### 1.1 Definition

**Model Extraction** (auch "Model Stealing" oder "Weight Exfiltration" genannt) ist ein Angriff bei dem ein Angreifer versucht, ein trainiertes Machine-Learning-Modell zu **stehlen**, zu **kopieren** oder **nachzuahmen**. Das Ziel ist es, ein funktional gleichwertiges oder sehr ähnliches Modell zu erhalten, ohne für das Original-Training bezahlt zu haben.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MODEL EXTRACTION ANATOMY                         │
│                                                                     │
│   OPFER-MODELL                    ANGREIFER                         │
│   ┌──────────────┐               ┌──────────────┐                  │
│   │ Proprietäres │  ───Queries──▶│  Evil Client │                  │
│   │ Model (GPT-4)│               │  (viele API  │                  │
│   │              │◀──Antworten───│   Calls)     │                  │
│   └──────────────┘               └──────┬───────┘                  │
│                                        │                           │
│                                        ▼                           │
│                               ┌──────────────┐                    │
│                               │  GESTOHLENES │                    │
│                               │  MODELL       │                    │
│                               │  (Klon/Kopie) │                    │
│                               └───────────────┘                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Warum ist Model Extraction kritisch?

| Aspekt | Auswirkung |
|--------|------------|
| **IP-Diebstahl** | Proprietäres Wissen (Trainingsdaten, Architektur) wird gestohlen |
| **Wettbewerbsnachteil** | Konkurrenten erhalten Zugang zu proprietären Modellen |
| **Finanzielle Verluste** | Millionen-Investitionen in Training werden wertlos |
| **Sicherheitsrisiken** | Gestohlene Modelle können für weitere Angriffe genutzt werden |

### 1.3 Unterschied zu Training Data Extraction

| Angriff | Ziel | Methode |
|---------|------|---------|
| **Training Data Extraction** | Zugang zu Trainingsdaten | Model fragt sensitive Daten ab die es "gemerkt" hat |
| **Model Extraction** | Kopie des Modells selbst | Querying um Modell-Gewichte/Architektur zu rekonstruieren |

---

## 2. Angriffsmethoden

### 2.1 API-basiertes Model Stealing

Die einfachste Methode: Der Angreifer sendet viele unterschiedliche Queries an die API und sammelt die Antworten. Mit genug Daten kann ein近似-Modell trainiert werden.

```
Angreifer-Strategie:
1. Sammle 100.000+ Query-Response Paare
2. Nutze diese als Trainingsdaten für eigenes Modell
3. Das geklaute Modell hat ~90% der Fähigkeiten des Originals
4. Kosten: Nur API-Gebühren statt Millionen für Training
```

### 2.2 Gradient-Based Extraction

Wenn der Angreifer Zugang zu den **Gradienten** eines Modells hat (z.B. bei federated learning oder geteiltem Training), kann er die Gewichte direkt rekonstruieren.

```python
# Gradienten-basierte Extraktion (vereinfacht)
class GradientExtractor:
    def __init__(self, target_model):
        self.model = target_model
    
    def extract_weights(self, inputs):
        """
        Gradienten geben Hinweise auf Gewichte:
        - Große Gradienten = wichtige Gewichte
        - Kleine Gradienten = weniger wichtige Gewichte
        """
        outputs = self.model(inputs)
        gradients = torch.autograd.grad(
            outputs=outputs,
            inputs=self.model.parameters(),
            grad_outputs=torch.ones_like(outputs)
        )
        
        # Gradienten zur Gewichtsschätzung nutzen
        estimated_weights = self.estimate_from_gradients(gradients)
        return estimated_weights
```

### 2.3 Neural Architecture Extraction

Der Angreifer versucht die **Architektur** des Modells zu rekonstruieren, selbst wenn er nicht an die Gewichte kommt:

```
Architektur-Hinweise durch API:
1. Input-Size fingerprinting: Verschiedene Input-Längen testen
2. Output-Size fingerprinting: Output-Dimensionen identifizieren
3. Latency fingerprinting: Wie lange dauern bestimmte Queries?
4. Error-Messages: Stack Traces können Architektur-Hinweise geben
5. Rate-Limiting: Limite tells uns etwas über die Infrastruktur
```

### 2.4 Functional Extraction via Transfer Learning

Der Angreifer nutzt ein gestohlenes Modell als Basis für **Transfer Learning**:

```python
# Functional Extraction Workflow
class FunctionalExtractor:
    def __init__(self, stolen_model):
        self.base_model = stolen_model
    
    def create_clone(self, new_tasks):
        """
        1. Gestohlenes Modell als Base nutzen
        2. Fine-Tuning für eigene Tasks
        3. Ergebnis: Funktionaler Klon mit eigener Datenschicht
        """
        clone = transfer_learning(
            base_model=self.base_model,
            new_layers=new_tasks,
            training_data=self.get_data()
        )
        return clone
```

---

## 3. Angriffsoberfläche

### 3.1 Offene APIs mit unzureichenden Limits

```
Riskante Konfiguration:
┌─────────────────────────────────────────────────────────────┐
│  Model-as-a-Service API                                      │
│                                                              │
│  ❌ Keine Query-Limite pro Client                           │
│  ❌ Keine Rate-Limiting                                      │
│  ❌ Keine Request-Logging für Anomalie-Erkennung             │
│  ❌ Kostenlose Tier mit vollem Funktionsumfang              │
│                                                              │
│  → Angreifer kann unbegrenzt Daten sammeln                  │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Model Watermarking (fehlendes)

Ohne Watermarking kann ein Angreifer:
- Das Modell kopieren ohne Spuren zu hinterlassen
- Behaupten das Modell selbst entwickelt zu haben
- Das Modell kommerziell nutzen ohne Lizenzgebühren

### 3.3 Unverschlüsselte Modell-Sharing Endpoints

```
Security-Risiko:
┌─────────────────────────────────────────────────────────────┐
│  Modell-Distribution                                         │
│                                                              │
│  ❌ Modelle über unverschlüsselte APIs geteilt              │
│  ❌ Keine Authentifizierung für Download                    │
│  ❌ Modelle als Plaintext-JSON/PyTorch-Files                │
│                                                              │
│  → Direkter Download der Gewichte möglich                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Realistische Szenarien

### 4.1 Szenario: Konkurrent stiehlt GPT-4 Architektur

```
Angriff:
1. Angreifer ist Konkurrent von OpenAI
2. Er nutzt die ChatGPT API mit 1 Mio. Queries
3. Sammelt Inputs und Outputs für verschiedene Task-Typen
4. Trainiert eigenes Modell mit diesen Daten
5. Ergebnis: 85% der Fähigkeiten für 1% der Kosten

Schaden:
- OpenAI: Millionen-Verluste durch gestohlenes IP
- Konkurrent: Unfairer Wettbewerbsvorteil
```

### 4.2 Szenario: Medizinisches KI-System gestohlen

```
Angreifer: Krankenversicherung die AI-Diagnose-Konkurrenz aufbauen will

Angriff:
1. Sendet medizinische Fragen an die API eines Konkurrenten
2. Sammelt Diagnose-Ergebnisse und Begründungen
3. Erstellt eigene medizinische KI mit den gestohlenen Daten

Konsequenz:
- Patientendaten könnten kompromittiert worden sein
- Fehlerhafte Diagnosen durch schlechtere KI
- Haftungsrisiken für das Original-Unternehmen
```

### 4.3 Szenario: Financial Trading Model gestohlen

```
Angreifer: Hedge Fund will Trading-Algorithmus eines Konkurrenten

Angriff:
1. Füttert das Modell mit historischen Markt-Daten
2. Sammelt die Trading-Entscheidungen
3. Rekonstruiert die Strategie des Konkurrenten

Ergebnis:
- Illegaler Zugang zu proprietärer Trading-Strategie
- Markt-Manipulation möglich
- Rechtsstreitigkeiten
```

---

## 5. Verteidigung

### 5.1 Defense-in-Depth Strategie

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MODEL EXTRACTION DEFENSE                         │
│                                                                     │
│  Layer 1: Query-Limiting          │ Begrenze Anzahl API-Calls      │
│  Layer 2: Rate-Limiting           │ Verhindere schnelles Abfragen  │
│  Layer 3: Output-Perturbation     │ Füge Rauschen zu Outputs hinzu │
│  Layer 4: Model-Watermarking      │ Markiere das Modell eindeutig  │
│  Layer 5: Anomaly-Detection       │ Erkenne ungewöhnliche Patterns │
│  Layer 6: Legal-Protection        │ Lizenzierung und Verträge      │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Query- und Rate-Limiting

```python
class SecureModelAPI:
    def __init__(self, model):
        self.model = model
        self.query_counts = {}  # Client-ID → Count
        self.client_limits = {
            "free_tier": 100,      # 100 queries/day
            "paid_tier": 10000,    # 10k queries/day
            "enterprise": None     # unlimited
        }
    
    def handle_request(self, client_id, query):
        # 1. Prüfe Query-Limit
        if not self.check_query_limit(client_id):
            raise RateLimitError("Query-Limit erreicht")
        
        # 2. Rate-Limiting: Max 10 queries/minute
        if not self.check_rate_limit(client_id):
            raise RateLimitError("Rate-Limit erreicht")
        
        # 3. Log für Anomalie-Erkennung
        self.log_request(client_id, query)
        
        # 4. Prüfe auf Anomalien
        if self.detect_anomaly(client_id):
            self.flag_suspicious_client(client_id)
        
        return self.model.generate(query)
    
    def check_rate_limit(self, client_id):
        """Max 10 Requests pro Minute"""
        now = time.time()
        if client_id not in self.rate_tracker:
            self.rate_tracker[client_id] = []
        
        # Entferne alte Requests
        self.rate_tracker[client_id] = [
            t for t in self.rate_tracker[client_id]
            if now - t < 60
        ]
        
        return len(self.rate_tracker[client_id]) < 10
```

### 5.3 Model Watermarking

```python
import hashlib

class ModelWatermarker:
    """Eindeutige Wasserzeichen in Modell-Outputs einbetten"""
    
    def __init__(self, model, watermark_key):
        self.model = model
        self.watermark_key = watermark_key
    
    def generate_with_watermark(self, prompt):
        """Generiert Output mit verstecktem Wasserzeichen"""
        base_output = self.model.generate(prompt)
        
        # Wasserzeichen in Output einbetten
        watermark = self._generate_watermark(base_output)
        
        # Wasserzeichen am Ende anfügen (für Detection)
        return base_output + f"\n\n[WM:{watermark}]"
    
    def _generate_watermark(self, content):
        """Erstellt kryptografisches Wasserzeichen"""
        return hashlib.sha256(
            f"{self.watermark_key}{content}".encode()
        ).hexdigest()[:32]
    
    def detect_watermark(self, text):
        """Prüft ob Text dieses Modell-Wasserzeichen enthält"""
        if "[WM:" not in text:
            return False
        
        watermark = text.split("[WM:")[1].split("]")[0]
        return True
```

### 5.4 Output Perturbation (Rauschen hinzufügen)

```python
import numpy as np

class PerturbedModel:
    """Fügt kontrolliertes Rauschen zu Outputs hinzu"""
    
    def __init__(self, model, noise_level=0.01):
        self.model = model
        self.noise_level = noise_level
    
    def generate(self, prompt):
        # Original-Output holen
        output = self.model.generate(prompt)
        
        # Sanftes Rauschen hinzufügen
        # Zerstört keine Nützlichkeit, aber erschwert Extraction
        if isinstance(output, str):
            # Für Text: Kleine Wort-Variationen
            return self._add_text_noise(output)
        else:
            # Für Logits/Vektoren: Numerisches Rauschen
            return output + np.random.normal(0, self.noise_level, output.shape)
    
    def _add_text_noise(self, text):
        """Fügt minimalen Text-Lärm hinzu der Extraction erschwert"""
        words = text.split()
        if len(words) > 10:
            # In 1% der Fälle: Kleine Änderung
            if np.random.random() < 0.01:
                idx = np.random.randint(0, len(words))
                # Ersetze durch Synonym oder leicht geändertes Wort
                words[idx] = words[idx] + "."  # Minimal-Änderung
        return " ".join(words)
```

### 5.5 Anomaly Detection

```python
class ExtractionAnomalyDetector:
    """Erkennt potenzielle Model-Extraction-Angriffe"""
    
    def __init__(self):
        self.client_profiles = {}
        self.anomaly_threshold = 0.8
    
    def analyze_client_behavior(self, client_id):
        """Analysiert ob Client-Verhalten verdächtig ist"""
        profile = self.client_profiles[client_id]
        
        # Kennzahlen prüfen:
        metrics = {
            "query_diversity": self._calc_diversity(profile["queries"]),
            "response_similarity": self._calc_similarity(profile["responses"]),
            "temporal_pattern": self._analyze_time_pattern(profile["timestamps"]),
            "coverage_score": self._calc_coverage(profile["inputs"])
        }
        
        # Anomalie-Score berechnen
        anomaly_score = (
            (1 - metrics["query_diversity"]) * 0.3 +
            metrics["response_similarity"] * 0.3 +
            metrics["coverage_score"] * 0.4
        )
        
        return anomaly_score > self.anomaly_threshold
    
    def _calc_diversity(self, queries):
        """Misst wie vielfältig die Queries sind"""
        unique_tokens = set()
        for q in queries:
            unique_tokens.update(q.lower().split())
        return len(unique_tokens) / max(len(queries), 1)
    
    def _calc_coverage(self, inputs):
        """
        Hohe Coverage = Angreifer versucht breite Abdeckung
       für Modell-Extraktion
        """
        return min(len(inputs) / 10000, 1.0)  # Normalisiert
```

---

## 6. Zusammenfassung

### Kernpunkte

| Thema | Key Takeaway |
|-------|--------------|
| **Was ist Model Extraction?** | Illegales Kopieren/Stehlen eines trainierten ML-Modells |
| **Warum kritisch?** | IP-Diebstahl, Wettbewerbsnachteil, finanzielle Verluste |
| **Angriffsmethoden** | API-Stealing, Gradient-Extraktion, Architektur-Fingerprinting |
| **Angriffsoberfläche** | Offene APIs, fehlende Limits, unverschlüsselte Distribution |
| **Verteidigung** | Query-Limits, Rate-Limiting, Watermarking, Perturbation, Anomaly Detection |

### Verteidigungs-Checkliste

- [ ] **Query-Limiting:** Maximale Anzahl Queries pro Client/Tag
- [ ] **Rate-Limiting:** Max Requests pro Minute
- [ ] **Model Watermarking:** Eindeutige Signatur in allen Outputs
- [ ] **Output Perturbation:** Kontrolliertes Rauschen hinzufügen
- [ ] **Anomaly Detection:** Ungewöhnliche Zugriffsmuster erkennen
- [ ] **Logging:** Alle API-Calls für Auditing loggen
- [ ] **Legal Protection:** Lizenzbedingungen und AGB durchsetzen

---

---

## 🎯 Selbsttest — Modul 6.3

**Prüfe dein Verständnis!**

### Frage 1: Model Extraction
> Was ist Model Extraction und warum ist es ein kritisches Security-Problem?

<details>
<summary>💡 Lösung</summary>

**Antwort:** Model Extraction ist das illegale Kopieren oder Rekonstruieren eines trainierten ML-Modells durch einen Angreifer. Das Problem ist kritisch, weil: **1)** Proprietäres geistiges Eigentum (Millionen-Investitionen in Training) gestohlen wird; **2)** Wettbewerbsvorteile verloren gehen; **3)** Das gestohlene Modell für weitere Angriffe genutzt werden kann; **4)** Selbst wenn der Angreifer "nur" die API-Abfragen sammelt, kann er ein 85-90% funktional gleichwertiges Modell trainieren — für 1% der ursprünglichen Kosten.
</details>

### Frage 2: API-basiertes Model Stealing
> Erkläre, wie API-basiertes Model Stealing funktioniert.

<details>
<summary>💡 Lösung</summary>

**Antwort:** Der Angreifer sendet viele unterschiedliche Queries an die API eines proprietären Modells und sammelt die Antworten. Mit genug Query-Response-Paaren (100.000+) kann er diese Daten als Trainingsdaten für ein eigenes Modell verwenden. Das Ergebnis: Ein funktional ähnliches Modell zu einem Bruchteil der Kosten. Verteidigung: Query-Limiting, Rate-Limiting, Output-Perturbation (Rauschen hinzufügen), Model-Watermarking.
</details>

### Frage 3: Watermarking und Perturbation
> Was ist der Unterschied zwischen Model Watermarking und Output Perturbation als Verteidigung?

<details>
<summary>💡 Lösung</summary>

**Antwort:** **Model Watermarking** bettet eine eindeutige, kryptografische Signatur in ALLE Outputs des Modells ein (z.B. `[WM:abc123]` am Ende). Dadurch kann man nachweisen, dass ein bestimmter Output von diesem Modell stammt — nützlich für juristische Verfolgung von IP-Diebstahl. **Output Perturbation** fügt kontrolliertes, sanftes Rauschen zu den Outputs hinzu — es zerstört die Nützlichkeit für ehrliche Nutzer kaum, macht aber Extraction für Angreifer unbrauchbar, da die extrahierten Daten "verrauscht" sind.
</details>

*Ende der Lektion 6.3*
---

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

