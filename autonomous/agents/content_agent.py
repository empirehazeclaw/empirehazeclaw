import os
#!/usr/bin/env python3
"""Content Agent - Creates human-like content with humor"""
import subprocess
import random
import sys
sys.path.insert(0, '/home/clawbot/.openclaw/workspace/scripts')
from humanize_content import process_text

# Human tweets with actual personality
HUMAN_TWEETS = [
    "KI ist wie ein Hund: Braucht Training, jault manchmal, aber ist loyal wenn man's richtig macht. 🐕",
    "Wer braucht Schlaf wenn man Kaffee hat? (Ich sag mal bis 3 Uhr...) ☕️",
    "Mein Trading Bot hat heute Gewinn gemacht. Ehrlich. Er hat mir 'ne Nachricht geschickt. Okay, war nur 'ne Exception. 🐛",
    "SaaS bauen: 10% Code, 90% Debuggen, 100% Kaffee. ☕️",
    "Die beste Feature? Ein Bug das keiner bemerkt. Features sind überbewertet. 😎",
    "Jeder sagt 'machst du SEO?' - Ja, mein SEO besteht aus beten. 🙏",
    "KI wird Jobs ersetzen. Hoffentlich meinen. Ich will Urlaub. 🌴",
    "Notion Templates: Weil Planung anfangs immer 80% vom Projekt ist. Der Rest? Implementierung. 😅",
]

BLOG_TOPICS = [
    ("Warum KI dich nicht ersetzt (aber deinen Job)", "ki-ersetzt-job"),
    ("Die Wahrheit über Trading Bots", "trading-wahrheit"),
    ("SaaS mit 0 Euro Starten - so hab ichs gemacht", "saas-0-euro"),
    ("Warum dein Template niemand kauft", "template-kauft-keiner"),
]

def create_blog_post():
    """Create human blog post"""
    topic, slug = random.choice(BLOG_TOPICS)
    
    # Get humanized content
    content = f"""
<!DOCTYPE html>
<html>
<head><title>{topic}</title></head>
<body style="font-family: system-ui; background: #0a0a0f; color: #fff; padding: 2rem; max-width: 800px; margin: 0 auto;">
<h1 style="color: #00ff88;">{topic}</h1>
<p>Mal ehrlich: Die meisten Guides sind langweilig. Dieser nicht.</p>

<h2>Der Deal</h2>
<p>Ich hab das selbst durchgemacht. Die Learnings teile ich hier.</p>

<h2>Was funktioniert hat</h2>
<p>Kurze Geschichte: Alles hat angefangen als ich...</p>

<h2>Was nicht funktioniert hat</h2>
<p>Und dann war da der Tag als ich dachte "Warum mache ich das eigentlich?"</p>

<h2>Fazit</h2>
<p>TL;DR: Einfach machen. Keine Perfektion. Learning by doing.</p>

<p style="color: #888; margin-top: 2rem;">—
Erstellt von jemandem der genau sochauso lernt wie du. 🚀</p>
</body>
</html>"""
    
    # Humanize it
    content = process_text(content, add_wit=True)
    
    filename = f"/var/www/empirehazeclaw-info/posts/{slug}.html"
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"✅ Created: {filename}")

def post_social():
    """Post human tweet"""
    tweet = random.choice(HUMAN_TWEETS)
    
    # Humanize first
    tweet = process_text(tweet, add_wit=True)
    
    result = subprocess.run(["xurl", "post", tweet], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Tweeted: {tweet[:50]}...")
    else:
        print(f"❌ Failed: {result.stderr}")

def run():
    print("✍️ Content Agent (Humanized) running...")
    create_blog_post()
    post_social()
    print("✅ Done!")

if __name__ == "__main__":
    run()
