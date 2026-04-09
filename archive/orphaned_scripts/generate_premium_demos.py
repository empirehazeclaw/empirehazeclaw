#!/usr/bin/env python3
"""Generate 75 Premium Demos - Stunning Design"""
import os

# 15 Branches with their themes
BRANCHES = [
    {"name": "fitness", "title": "FITNESS ELITE", "tag": "🔴", "primary": "#ff4d4d", "accent": "#ffd700",
     "hero": "TRANSFORMIERE DEINEN KÖRPER", "features": ["Premium Ausstattung", "Persönliche Betreuung", "Modernste Kurse"]},
    {"name": "restaurant", "title": "LE CUISINE", "tag": "🍽️", "primary": "#d4af37", "accent": "#8b4513",
     "hero": "KULINARISCHE REISEN", "features": ["Fine Dining", "Frische Zutaten", "Exklusive Atmosphäre"]},
    {"name": "friseur", "title": "HAIR ELITE", "tag": "💇", "primary": "#e91e63", "accent": "#fce4ec",
     "hero": "YOUR STYLE. YOUR LOOK.", "features": ["Top-Stylisten", "Premium Produkte", "Exklusive Cuts"]},
    {"name": "arztpraxis", "title": "HEALTH ELITE", "tag": "🏥", "primary": "#00bcd4", "accent": "#006064",
     "hero": "IHRE GESUNDHEIT. UNSERE PRIORITÄT.", "features": ["Modernste Medizin", "Erfahrene Ärzte", "Individuelle Betreuung"]},
    {"name": "café", "title": "CAFÉ ELITE", "tag": "☕", "primary": "#8d6e63", "accent": "#d7ccc8",
     "hero": "GENUSSMOMENTE PUR", "features": ["Premium Kaffee", "Hausgemachte Backwaren", "Gemütliche Atmosphäre"]},
    {"name": "kosmetik", "title": "BEAUTY ELITE", "tag": "💅", "primary": "#e91e63", "accent": "#f8bbd0",
     "hero": "SCHÖNHEIT VERPFLICHTET", "features": ["Luxus-Behandlungen", "Premium Produkte", "Entspannung total"]},
    {"name": "optiker", "title": "VISION ELITE", "tag": "👓", "primary": "#3f51b5", "accent": "#c5cae9",
     "hero": "BESSER SEHEN. BESSER LEBEN.", "features": ["Top-Marken", "Moderne Technik", "Individuelle Beratung"]},
    {"name": "physiotherapie", "title": "THERAPIE ELITE", "tag": "💪", "primary": "#4caf50", "accent": "#c8e6c9",
     "hero": "BEWEGLICHKEIT IST LEBEN", "features": ["Erfahrene Therapeuten", "Moderne Methoden", "Ganzheitliche Betreuung"]},
    {"name": "autohaus", "title": "AUTO ELITE", "tag": "🚗", "primary": "#607d8b", "accent": "#cfd8dc",
     "hero": "IHR TRAUMWAGEN. UNSERE LEIDENSCHAFT.", "features": ["Top-Marken", "Garantie", "Premium Service"]},
    {"name": "elektriker", "title": "POWER ELITE", "tag": "⚡", "primary": "#ffc107", "accent": "#ff9800",
     "hero": "STROM. SICHERHEIT. KOMPETENZ.", "features": ["Sofort-Service", "Zertifizierte Experten", "24/7 Notfall"]},
    {"name": "klempner", "title": "WASSER ELITE", "tag": "🚿", "primary": "#2196f3", "accent": "#90caf9",
     "hero": "FLUSS IM HAUS. PROBLEME RAUS.", "features": ["Sofort-Service", "Moderne Technik", "Saubere Arbeit"]},
    {"name": "maler", "title": "FARBE ELITE", "tag": "🎨", "primary": "#9c27b0", "accent": "#e1bee7",
     "hero": "FARBE FÜRS LEBEN", "features": ["Premium Farben", "Professionelle Arbeit", "Sauber & Schnell"]},
    {"name": "zahnarzt", "title": "DENTAL ELITE", "tag": "🦷", "primary": "#00bcd4", "accent": "#b2ebf2",
     "hero": "GESUNDE ZÄHNE. STRAHLENDES LÄCHELN.", "features": ["Schmerzfrei", "Modernste Technik", "Angstfrei"]},
    {"name": "rechtsanwalt", "title": "LEGAL ELITE", "tag": "⚖️", "primary": "#37474f", "accent": "#90a4ae",
     "hero": "IHR RECHT. UNSERE KOMPETENZ.", "features": ["Erfahrene Anwälte", "Individuelle Strategie", "Erfolgsaussichten"]},
    {"name": "gärtnerei", "title": "GRÜN ELITE", "tag": "🌱", "primary": "#4caf50", "accent": "#c8e6c9",
     "hero": "GRÜNE OASEN PLANEN", "features": ["Professionelle Planung", "Pflege-Service", "Nachhaltig"]},
]

# 5 Styles
STYLES = [
    {"name": "red", "primary": "#ff4d4d", "bg": "#0a0a0a", "gradient": "linear-gradient(135deg, #ff4d4d 0%, #ff8a00 100%)"},
    {"name": "blue", "primary": "#2196f3", "bg": "#0a0a1a", "gradient": "linear-gradient(135deg, #2196f3 0%, #00bcd4 100%)"},
    {"name": "gold", "primary": "#d4af37", "bg": "#0a0a0a", "gradient": "linear-gradient(135deg, #d4af37 0%, #f4e04d 100%)"},
    {"name": "green", "primary": "#4caf50", "bg": "#0a0f0a", "gradient": "linear-gradient(135deg, #4caf50 0%, #8bc34a 100%)"},
    {"name": "purple", "primary": "#9c27b0", "bg": "#0a0a1a", "gradient": "linear-gradient(135deg, #9c27b0 0%, #e91e63 100%)"},
]

for branch in BRANCHES:
    for style in STYLES:
        html = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{branch['title']} - Premium</title>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root {{
            --primary: {style['primary']};
            --bg: {style['bg']};
            --gradient: {style['gradient']};
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Outfit', sans-serif; background: var(--bg); color: white; overflow-x: hidden; }}
        .hero-bg {{ position: fixed; inset: 0; background: radial-gradient(ellipse at 20% 80%, {style['primary']}22 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, {style['primary']}11 0%, transparent 50%), var(--bg); z-index: 0; }}
        .hero-bg::before {{ content: ''; position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px); background-size: 50px 50px; }}
        header {{ position: fixed; top: 0; left: 0; right: 0; z-index: 1000; padding: 1.5rem 5%; display: flex; justify-content: space-between; align-items: center; background: rgba(10,10,10,0.9); backdrop-filter: blur(20px); }}
        .logo {{ font-family: 'Bebas Neue', sans-serif; font-size: 1.8rem; letter-spacing: 3px; }}
        .logo span {{ color: var(--primary); }}
        .cta {{ background: var(--gradient); color: white; padding: 0.8rem 2rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; border: none; cursor: pointer; }}
        .hero {{ min-height: 100vh; display: flex; align-items: center; padding: 0 5%; position: relative; z-index: 1; }}
        .hero-content {{ max-width: 800px; }}
        .hero-badge {{ display: inline-block; background: {style['primary']}22; border: 1px solid var(--primary); color: var(--primary); padding: 0.5rem 1.5rem; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 2rem; }}
        .hero h1 {{ font-family: 'Bebas Neue', sans-serif; font-size: clamp(3rem, 8vw, 6rem); line-height: 0.95; margin-bottom: 1.5rem; background: linear-gradient(135deg, #fff 0%, #ccc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .hero p {{ font-size: 1.2rem; color: #888; max-width: 500px; margin-bottom: 2.5rem; line-height: 1.8; }}
        .btn-primary {{ background: var(--gradient); color: white; padding: 1.2rem 3rem; font-size: 1rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; border: none; cursor: pointer; transition: all 0.3s; }}
        .btn-primary:hover {{ transform: translateY(-5px); box-shadow: 0 20px 40px {style['primary']}44; }}
        .features {{ padding: 8rem 5%; }}
        .section-title {{ text-align: center; margin-bottom: 4rem; }}
        .section-title h2 {{ font-family: 'Bebas Neue', sans-serif; font-size: 3rem; margin-bottom: 1rem; }}
        .features-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }}
        .feature-card {{ background: #111; padding: 3rem; border: 1px solid rgba(255,255,255,0.05); transition: all 0.5s; position: relative; }}
        .feature-card::before {{ content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 3px; background: var(--gradient); transform: scaleX(0); transform-origin: left; transition: transform 0.5s; }}
        .feature-card:hover {{ transform: translateY(-10px); border-color: var(--primary); }}
        .feature-card:hover::before {{ transform: scaleX(1); }}
        .feature-icon {{ width: 60px; height: 60px; background: {style['primary']}22; display: flex; align-items: center; justify-content: center; margin-bottom: 1.5rem; font-size: 1.5rem; color: var(--primary); }}
        .feature-card h3 {{ font-size: 1.3rem; margin-bottom: 1rem; }}
        .feature-card p {{ color: #666; line-height: 1.7; }}
        .cta-section {{ padding: 8rem 5%; text-align: center; background: radial-gradient(ellipse at center, {style['primary']}11 0%, transparent 70%); }}
        .cta-section h2 {{ font-family: 'Bebas Neue', sans-serif; font-size: 3.5rem; margin-bottom: 1rem; }}
        .price-tag {{ font-size: 4rem; font-weight: 700; color: var(--primary); margin-bottom: 2rem; }}
        .price-tag span {{ font-size: 1.5rem; color: #666; }}
        footer {{ padding: 3rem 5%; text-align: center; border-top: 1px solid rgba(255,255,255,0.05); color: #666; }}
        @media (max-width: 768px) {{ .hero-buttons {{ flex-direction: column; }} }}
    </style>
</head>
<body>
    <div class="hero-bg"></div>
    <header>
        <div class="logo">{branch['title']}<span></span></div>
        <button class="cta">Kontakt</button>
    </header>
    <section class="hero">
        <div class="hero-content">
            <div class="hero-badge">{branch['tag']} Willkommen</div>
            <h1>{branch['hero']}</h1>
            <p>Erleben Sie {branch['title'].lower()} auf höchstem Niveau. Qualität, die überzeugt. Service, der begeistert.</p>
            <button class="btn-primary">Kostenlos beraten</button>
        </div>
    </section>
    <section class="features">
        <div class="section-title">
            <h2>UNSERE LEISTUNGEN</h2>
            <p>Exzellenz in jedem Detail</p>
        </div>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-star"></i></div>
                <h3>{branch['features'][0]}</h3>
                <p>Erstklassige Qualität in allen Bereichen. Keine Kompromisse.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-users"></i></div>
                <h3>{branch['features'][1]}</h3>
                <p>Erfahrene Profis die Sie bis zum Ziel begleiten.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon"><i class="fas fa-heart"></i></div>
                <h3>{branch['features'][2]}</h3>
                <p>Ihre Zufriedenheit ist unser höchstes Gut.</p>
            </div>
        </div>
    </section>
    <section class="cta-section">
        <h2>BEREIT FÜR DEN START?</h2>
        <p>Professionelle Qualität zu fairen Preisen.</p>
        <div class="price-tag">€199<span>/einmalig</span></div>
        <button class="btn-primary">Jetzt anfragen</button>
    </section>
    <footer><p>© 2026 {branch['title']} - Alle Rechte vorbehalten.</p></footer>
</body>
</html>'''
        
        filename = f"{branch['name']}-{style['name']}.html"
        with open(f"projects/local-closer/demos-premium/{filename}", "w") as f:
            f.write(html)
        print(f"✅ {filename}")

print(f"\n✅ 75 PREMIUM DEMOS GENERATED!")
