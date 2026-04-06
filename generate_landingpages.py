#!/usr/bin/env python3
"""
Landing Page Generator for Local Closer
Generates 5 style variations for 15 branches
"""
import json
import os
import random
from datetime import datetime

# Branch data
BRANCHES = [
    {"name": "Fitnessstudio", "icon": "dumbbell", "tagline": "Fitness für Alle"},
    {"name": "Restaurant", "icon": "utensils", "tagline": "Kulinarische Erlebnisse"},
    {"name": "Arztpraxis", "icon": "user-md", "tagline": "Ihre Gesundheit ist uns wichtig"},
    {"name": "Zahnarzt", "icon": "tooth", "tagline": "Gesunde Zähne, strahlendes Lächeln"},
    {"name": "Physiotherapie", "icon": "hands", "tagline": "Beweglich durchs Leben"},
    {"name": "Friseur", "icon": "scissors", "tagline": "Style, der begeistert"},
    {"name": "Kosmetik", "icon": "spa", "tagline": "Natürliche Schönheit"},
    {"name": "Bäckerei", "icon": "bread-slice", "tagline": "Frisch aus dem Ofen"},
    {"name": "Café", "icon": "coffee", "tagline": "Genussmomente pur"},
    {"name": "Gärtnerei", "icon": "seedling", "tagline": "Grüne Oasen gestalten"},
    {"name": "Elektriker", "icon": "bolt", "tagline": "Elektrische Kompetenz"},
    {"name": "Klempner", "icon": "droplet", "tagline": "Sanitär vom Profi"},
    {"name": "Maler", "icon": "paint-roller", "tagline": "Farbe für Ihr Zuhause"},
    {"name": "Autohaus", "icon": "car", "tagline": "Ihr vertrauenswürdiger Partner"},
    {"name": "Optiker", "icon": "glasses", "tagline": "Besser sehen, besser leben"}
]

# Styles
STYLES = [
    {"name": "Classic", "primary": "#1a1a2e", "secondary": "#16213e", "accent": "#e94560", "accent_sec": "#ff6b6b", "bg": "#ffffff", "bg_alt": "#f8f9fa", "text": "#1f1f1f", "text_light": "#6b7280", "font_display": "Playfair Display, serif", "font_body": "Inter, sans-serif", "radius": "8", "shadow": "0 4px 15px rgba(0,0,0,0.08)", "icon": "star"},
    {"name": "Modern", "primary": "#0f172a", "secondary": "#1e293b", "accent": "#3b82f6", "accent_sec": "#60a5fa", "bg": "#ffffff", "bg_alt": "#f1f5f9", "text": "#1e293b", "text_light": "#64748b", "font_display": "Inter, sans-serif", "font_body": "Inter, sans-serif", "radius": "12", "shadow": "0 10px 30px rgba(0,0,0,0.1)", "icon": "bolt"},
    {"name": "Elegant", "primary": "#2d1f3d", "secondary": "#4a2c6a", "accent": "#8b5cf6", "accent_sec": "#a78bfa", "bg": "#faf5ff", "bg_alt": "#f3e8ff", "text": "#1f1f1f", "text_light": "#6b7280", "font_display": "Playfair Display, serif", "font_body": "Inter, sans-serif", "radius": "16", "shadow": "0 20px 40px rgba(139,92,246,0.15)", "icon": "gem"},
    {"name": "Minimal", "primary": "#18181b", "secondary": "#27272a", "accent": "#10b981", "accent_sec": "#34d399", "bg": "#ffffff", "bg_alt": "#fafafa", "text": "#18181b", "text_light": "#71717a", "font_display": "Inter, sans-serif", "font_body": "Inter, sans-serif", "radius": "4", "shadow": "0 2px 10px rgba(0,0,0,0.05)", "icon": "leaf"},
    {"name": "Bold", "primary": "#000000", "secondary": "#1a1a1a", "accent": "#f59e0b", "accent_sec": "#fbbf24", "bg": "#ffffff", "bg_alt": "#fffbeb", "text": "#111111", "text_light": "#525252", "font_display": "Inter, sans-serif", "font_body": "Inter, sans-serif", "radius": "0", "shadow": "8px 8px 0px rgba(0,0,0,0.1)", "icon": "fire"}
]

# Base template
BASE_TEMPLATE = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{COMPANY}} - Professionelle Website</title>
    <meta name="description" content="{{COMPANY}} in {{CITY}}. Professionelle {{BRANCH}} Dienstleistungen.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root {
            --primary: {{PRIMARY}};
            --secondary: {{SECONDARY}};
            --accent: {{ACCENT}};
            --accent-sec: {{ACCENT_SEC}};
            --bg: {{BG}};
            --bg-alt: {{BG_ALT}};
            --text: {{TEXT}};
            --text-light: {{TEXT_LIGHT}};
            --gradient: linear-gradient(135deg, {{ACCENT}} 0%, {{ACCENT_SEC}} 100%);
            --font-display: {{FONT_DISPLAY}};
            --font-body: {{FONT_BODY}};
            --radius: {{RADIUS}}px;
            --shadow: {{SHADOW}};
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: var(--font-body); background: var(--bg); color: var(--text); line-height: 1.6; }
        h1, h2, h3 { font-family: var(--font-display); font-weight: 700; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        header { background: var(--bg); padding: 1rem 0; border-bottom: 1px solid rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
        .header-inner { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: 700; color: var(--primary); text-decoration: none; display: flex; align-items: center; gap: 0.5rem; }
        .logo i { color: var(--accent); }
        
        .btn { display: inline-block; padding: 1rem 2rem; border-radius: var(--radius); font-weight: 600; text-decoration: none; transition: all 0.3s; }
        .btn-primary { background: var(--gradient); color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.3); }
        
        .hero { padding: 6rem 0; background: var(--bg-alt); text-align: center; }
        .hero h1 { font-size: 3rem; color: var(--primary); margin-bottom: 1rem; }
        .hero p { font-size: 1.25rem; color: var(--text-light); max-width: 600px; margin: 0 auto 2rem; }
        .tagline { display: inline-block; background: var(--gradient); color: white; padding: 0.5rem 1.5rem; border-radius: 50px; font-weight: 600; margin-bottom: 1rem; }
        
        .features { padding: 4rem 0; }
        .features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; margin-top: 3rem; }
        .feature-card { padding: 2rem; background: var(--bg); border-radius: var(--radius); box-shadow: var(--shadow); text-align: center; }
        .feature-card i { font-size: 2rem; color: var(--accent); margin-bottom: 1rem; }
        
        .about { padding: 4rem 0; background: var(--bg-alt); }
        .about-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4rem; align-items: center; }
        .about-list { list-style: none; margin-top: 1.5rem; }
        .about-list li { padding: 0.5rem 0; display: flex; align-items: center; gap: 0.75rem; }
        .about-list li i { color: var(--accent); }
        
        .contact { padding: 4rem 0; text-align: center; }
        .contact-card { background: var(--bg); padding: 3rem; border-radius: var(--radius); box-shadow: var(--shadow); max-width: 600px; margin: 2rem auto 0; }
        .contact-info { display: flex; justify-content: center; gap: 3rem; flex-wrap: wrap; margin-top: 1.5rem; }
        
        footer { background: var(--primary); color: white; padding: 2rem 0; text-align: center; }
        
        @media (max-width: 768px) {
            .features-grid { grid-template-columns: 1fr; }
            .about-grid { grid-template-columns: 1fr; }
            .hero h1 { font-size: 2rem; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container header-inner">
            <a href="#" class="logo"><i class="fas fa-{{ICON}}"></i> {{COMPANY}}</a>
            <a href="#contact" class="btn btn-primary">Kontakt</a>
        </div>
    </header>

    <section class="hero">
        <div class="container">
            <span class="tagline">{{TAGLINE}}</span>
            <h1>{{HEADLINE}}</h1>
            <p>{{SUBHEADLINE}}</p>
            <a href="#contact" class="btn btn-primary">Kostenloses Angebot anfordern</a>
        </div>
    </section>

    <section class="features">
        <div class="container">
            <h2 style="text-align: center; font-size: 2rem; color: var(--primary);">Unsere Leistungen</h2>
            <div class="features-grid">
                <div class="feature-card"><i class="fas fa-{{ICON}}"></i><h3>{{FEATURE1}}</h3></div>
                <div class="feature-card"><i class="fas fa-{{ICON2}}"></i><h3>{{FEATURE2}}</h3></div>
                <div class="feature-card"><i class="fas fa-{{ICON3}}"></i><h3>{{FEATURE3}}</h3></div>
            </div>
        </div>
    </section>

    <section class="about">
        <div class="container">
            <div class="about-grid">
                <div>
                    <h2>Über uns</h2>
                    <p>{{ABOUT}}</p>
                    <ul class="about-list">
                        <li><i class="fas fa-check"></i> {{POINT1}}</li>
                        <li><i class="fas fa-check"></i> {{POINT2}}</li>
                        <li><i class="fas fa-check"></i> {{POINT3}}</li>
                    </ul>
                </div>
                <div style="background: var(--bg); padding: 2rem; border-radius: var(--radius);">
                    <p style="color: var(--text-light); font-style: italic;">"{{TESTIMONIAL}}"</p>
                </div>
            </div>
        </div>
    </section>

    <section class="contact" id="contact">
        <div class="container">
            <h2>Jetzt professionelle Website sichern!</h2>
            <div class="contact-card">
                <h3 style="color: var(--accent); font-size: 1.5rem;">199€ Einmalig</h3>
                <p style="margin: 1rem 0;">+ 29€/Monat Hosting inklusive</p>
                <a href="#" class="btn btn-primary">Jetzt anfragen</a>
                <div class="contact-info">
                    <div><i class="fas fa-phone"></i> {{PHONE}}</div>
                    <div><i class="fas fa-envelope"></i> {{EMAIL}}</div>
                    <div><i class="fas fa-map-marker-alt"></i> {{ADDRESS}}</div>
                </div>
            </div>
        </div>
    </section>

    <footer>
        <div class="container"><p>&copy; 2026 {{COMPANY}}</p></div>
    </footer>
</body>
</html>"""

def generate_page(branch, style, version, output_dir):
    """Generate a landing page"""
    # Placeholder values
    city = random.choice(["Berlin", "Hamburg", "München", "Köln", "Frankfurt"])
    company = f"{branch['name']} {city}"
    
    replacements = {
        "{{COMPANY}}": company,
        "{{CITY}}": city,
        "{{BRANCH}}": branch["name"].lower(),
        "{{TAGLINE}}": branch["tagline"],
        "{{HEADLINE}}": f"Professionelle Website für Ihr {branch['name']}",
        "{{SUBHEADLINE}}": f"Ihre lokale {branch['name']}-Praxis in {city}. Modern, professionell und immer erreichbar.",
        "{{ICON}}": branch["icon"],
        "{{ICON2}}": "clock",
        "{{ICON3}}": "heart",
        "{{FEATURE1}}": "Individuelles Design",
        "{{FEATURE2}}": "Mobile Optimiert",
        "{{FEATURE3}}": "SEO Optimiert",
        "{{ABOUT}}": f"Seit über 10 Jahren ist {company} Ihr vertrauenswürdiger Partner für {branch['name'].lower()} Dienstleistungen in {city}.",
        "{{POINT1}}": "10+ Jahre Erfahrung",
        "{{POINT2}}": "500+ zufriedene Kunden",
        "{{POINT3}}": "100% Zufriedenheitsgarantie",
        "{{TESTIMONIAL}}": "Die neue Website hat uns viele neue Kunden gebracht. Sehr zu empfehlen!",
        "{{PHONE}}": "+49 123 456789",
        "{{EMAIL}}": "info@beispiel.de",
        "{{ADDRESS}}": f"Hauptstraße 1, {city}",
        # Style variables
        "{{PRIMARY}}": style["primary"],
        "{{SECONDARY}}": style["secondary"],
        "{{ACCENT}}": style["accent"],
        "{{ACCENT_SEC}}": style["accent_sec"],
        "{{BG}}": style["bg"],
        "{{BG_ALT}}": style["bg_alt"],
        "{{TEXT}}": style["text"],
        "{{TEXT_LIGHT}}": style["text_light"],
        "{{FONT_DISPLAY}}": style["font_display"],
        "{{FONT_BODY}}": style["font_body"],
        "{{RADIUS}}": style["radius"],
        "{{SHADOW}}": style["shadow"],
        "{{ICON}}": style["icon"]
    }
    
    # Generate HTML
    html = BASE_TEMPLATE
    for key, value in replacements.items():
        html = html.replace(key, value)
    
    # Save file
    filename = f"{branch['name'].lower().replace(' ', '-')}-{style['name'].lower()}.html"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filename

def main():
    output_dir = "projects/local-closer/demos-v4"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"=== 🎨 GENERATING LANDING PAGES ===")
    
    # Generate 5 styles for first 15 branches
    count = 0
    for branch in BRANCHES[:15]:
        for style in STYLES:
            filename = generate_page(branch, style, count, output_dir)
            count += 1
            print(f"  ✅ {filename}")
    
    print(f"\n✅ TOTAL: {count} landing pages generated!")
    print(f"📁 Output: {output_dir}/")

if __name__ == "__main__":
    main()
