import sys
import os
import json
from datetime import datetime
import subprocess

sys.path.insert(0, '/home/clawbot/.openclaw/workspace/scripts')
from humanize_content import process_text

BLOG_DIR = "/var/www/empirehazeclaw-info/posts/en"
SOCIAL_LOG = "/home/clawbot/.openclaw/workspace/data/posted_blogs.json"

def load_posted():
    if os.path.exists(SOCIAL_LOG):
        with open(SOCIAL_LOG, 'r') as f:
            return json.load(f)
    return []

def save_posted(posted):
    with open(SOCIAL_LOG, 'w') as f:
        json.dump(posted, f)

def get_latest_unposted_blog():
    posted = load_posted()
    
    # Finde alle .html Dateien in /en/
    if not os.path.exists(BLOG_DIR): return None
    
    files = [f for f in os.listdir(BLOG_DIR) if f.endswith('.html')]
    # Sortiere nach Erstellungsdatum
    files.sort(key=lambda x: os.path.getmtime(os.path.join(BLOG_DIR, x)), reverse=True)
    
    for f in files:
        if f not in posted:
            return f
    return None

def create_social_post(blog_file):
    # Einfache Extraktion: Nimm den Titel aus der Datei (oder Dateinamen)
    title = blog_file.replace('.html', '').replace('-', ' ').title()
    link = f"https://empirehazeclaw.info/posts/en/{blog_file}"
    
    base_text = f"I just published a new article: '{title}'. If you're building SaaS or automating workflows, you need to read this."
    
    # Nutze Humanizer + Humor
    humanized = process_text(base_text, add_wit=True)
    
    tweet = f"{humanized}\n\nRead the full breakdown here: {link}"
    return tweet

def run_content_loop():
    print(f"[{datetime.now().isoformat()}] 🔄 Starte Social-Media Content Loop")
    
    blog_file = get_latest_unposted_blog()
    if not blog_file:
        print("Kein neuer Blogpost zum Recyclen gefunden.")
        return
        
    print(f"Recycle Blogpost: {blog_file}")
    tweet = create_social_post(blog_file)
    print(f"Generierter Tweet:\n{tweet}")
    
    # Posten via xurl (Vorsicht: X API limitiert / 403)
    try:
        print("Versuche auf X zu posten...")
        result = subprocess.run(["xurl", "post", tweet], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Erfolgreich gepostet!")
        else:
            print(f"⚠️ X API Fehler (403?): {result.stderr.strip()} (Wird trotzdem als verarbeitet markiert, um Schleifen zu vermeiden)")
            
        # Als gepostet markieren
        posted = load_posted()
        posted.append(blog_file)
        save_posted(posted)
        
    except Exception as e:
        print(f"Kritischer Fehler beim Posten: {e}")

if __name__ == "__main__":
    run_content_loop()
