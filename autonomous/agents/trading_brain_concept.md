# Verbesserungen für den Trading Bot (Bevor wir ihn aktivieren)

Bevor wir den Agenten blind mit virtuellem Geld (Paper Trading) handeln lassen, müssen wir sein "Gehirn" und die Infrastruktur deutlich robuster und intelligenter machen. 

Hier sind 4 Architektur-Verbesserungen, die wir morgen umsetzen sollten:

## 1. Technischer Indikator-Stack (TA-Lib)
**Aktuell:** Er kennt nur den aktuellen Preis (Spot-Price via CoinGecko).
**Verbesserung:** Wir integrieren Bibliotheken wie `pandas-ta` oder `ta` (Technical Analysis). Der Bot braucht Zugriff auf historische Candlestick-Daten (OHLCV) z.B. von Binance (kostenlose Public API), um:
- **RSI (Relative Strength Index):** Ist der Markt überkauft/überverkauft?
- **MACD (Moving Average Convergence Divergence):** Dreht der Trend?
- **Bollinger Bands:** Wie volatil ist der Markt?

## 2. Der "Sentiment-Scraper" (News & Twitter)
**Aktuell:** Keine Marktstimmung.
**Verbesserung:** Krypto-Märkte reagieren massiv auf News. Unser Researcher-Agent sollte alle 6 Stunden Headlines scrapen (z.B. über kostenlose RSS Feeds von CoinTelegraph oder Reddit r/CryptoCurrency) und durch unser LLM (Gemini 3.1 Pro) jagen, um einen **"Fear & Greed" Sentiment-Score (-100 bis +100)** zu berechnen.

## 3. Die hybride Strategie-Engine (Das eigentliche Gehirn)
**Aktuell:** Dummy-Routen für Strategien existieren, machen aber nichts.
**Verbesserung:** Wir bauen die `trading_agent.py` so auf, dass sie Entscheidungen nur trifft, wenn **beide** Signale übereinstimmen:
- *Beispiel Trade:* RSI ist unter 30 (überverkauft, starkes Kaufsignal) UND der Sentiment-Score ist > +20 (positive Nachrichtenlage) -> **EXECUTE BUY**.

## 4. Risk Management (Stop-Loss / Take-Profit)
**Aktuell:** Wenn er kauft, behält er es, bis er wieder den Befehl zum Verkaufen bekommt.
**Verbesserung:** Jeder Trade *muss* automatisch einen harten Stop-Loss (z.B. -5%) und einen Take-Profit (z.B. +15%) mitbekommen. Fällt der Preis, wird gnadenlos liquidiert. So überlebt das Portfolio Flash-Crashes.

---
**Der Plan für morgen:**
Wir schreiben nicht nur ein stupides Skript, das zufällig kauft, sondern wir bauen ihm morgen einen echten "Data-Pipeline"-Agenten, der zuerst TA-Signale und News-Sentiments sammelt, bevor er den Trade-Befehl an die API (Port 8001) schickt.
