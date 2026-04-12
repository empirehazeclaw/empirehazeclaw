import feedparser
import requests
import json
import re
import os

def get_llm_api_key():
    try:
        with open(os.path.expanduser('~/.openclaw/openclaw.json'), 'r') as f:
            cfg = json.load(f)
            # Try to get openrouter key
            for key, val in cfg.get('auth', {}).get('profiles', {}).items():
                if 'openrouter' in key.lower() or 'openrouter' in val.get('provider', '').lower():
                    return val.get('apiKey'), 'openrouter'
                if 'google' in key.lower() or 'google' in val.get('provider', '').lower():
                    return val.get('apiKey'), 'google'
    except:
        pass
    return None, None

def analyze_sentiment():
    """Liest RSS Feeds und analysiert die Marktstimmung mit LLM (Fallback: Advanced Keywords)"""
    print("  📰 Lade Krypto-News (CoinTelegraph)...")
    feed = feedparser.parse('https://cointelegraph.com/rss')
    
    headlines = [entry.title for entry in feed.entries[:15]]
    news_text = "\n".join(f"- {h}" for h in headlines)
    
    api_key, provider = get_llm_api_key()
    score = 0
    
    # LLM Sentiment Analysis (Wenn API Key gefunden)
    if api_key and provider == 'openrouter':
        try:
            print("  🧠 Analysiere Sentiment via LLM (OpenRouter)...")
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "google/gemini-3.1-pro-preview", # oder fallback
                    "messages": [{
                        "role": "user", 
                        "content": f"Analyze these crypto headlines. Reply ONLY with a single number between -100 (extreme fear/bearish) and 100 (extreme greed/bullish). No other text.\n\n{news_text}"
                    }]
                },
                timeout=10
            )
            content = res.json()['choices'][0]['message']['content'].strip()
            numbers = re.findall(r'-?\d+', content)
            if numbers:
                score = int(numbers[0])
                print(f"  🧠 LLM Score erfolgreich extrahiert: {score}")
                return get_signal_from_score(score)
        except Exception as e:
            print(f"  ⚠️ LLM Analyse fehlgeschlagen ({e}), nutze Fallback...")
    
    # Fallback: Advanced Keyword Scoring
    print("  🧮 Nutze NLP Keyword-Scoring...")
    bullish_words = ['surge', 'jump', 'bull', 'high', 'adopt', 'approve', 'launch', 'gain', 'positive', 'up', 'soar', 'record', 'buy', 'upgrade', 'breakout']
    bearish_words = ['crash', 'drop', 'bear', 'low', 'ban', 'reject', 'hack', 'loss', 'negative', 'down', 'scam', 'plunge', 'sell', 'downgrade', 'liquidate']

    for title in headlines:
        title_lower = title.lower()
        bull_count = sum(1 for w in bullish_words if re.search(r'\b' + w + r'\b', title_lower))
        bear_count = sum(1 for w in bearish_words if re.search(r'\b' + w + r'\b', title_lower))
        score += (bull_count * 12)
        score -= (bear_count * 12)

    score = max(-100, min(100, score))
    return get_signal_from_score(score)

def get_signal_from_score(score):
    signal = "NEUTRAL"
    if score >= 20: signal = "BULLISH"
    if score <= -20: signal = "BEARISH"
    
    return {
        "score": score,
        "signal": signal
    }
