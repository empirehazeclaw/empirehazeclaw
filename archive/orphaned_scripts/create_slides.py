#!/usr/bin/env python3
"""
TikTok Slide Generator für AI Hosting B2B
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Slide config
WIDTH, HEIGHT = 1080, 1920
FPS = 1
DURATION_PER_SLIDE = 3  # seconds

SLIDES = [
    ("Business:", "Zu teuer für", "24/7 Support?"),
    ("Unsere KI übernimmt:", "Sofort, überall,", "jede Sprache"),
    ("E-Commerce? SaaS?", "Agenturen?", "→Passt zu jedem Business"),
    ("€99/Monat", "statt €500/Monat", "für Personal"),
    ("Setup in 5 Minuten:", "Keine Technik-", "Kenntnisse nötig"),
    ("EmpireHazeClaw.com/store", "AI Chatbot mieten", ""),
]

# Colors - Dark theme met our brand
BG_COLOR = (13, 17, 23)  # Dark
TEXT_COLOR = (255, 255, 255)  # White
ACCENT_COLOR = (0, 255, 136)  # Green accent

OUTPUT_DIR = "/home/clawbot/.openclaw/workspace/tiktok-slideshow/input-ai-hosting"

def create_slide(slide_num, lines):
    """Create a single slide image"""
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Calculate font size based on text length
    max_len = max(len(line) for line in lines if line)
    font_size = 120 if max_len < 15 else 80
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
    except:
        font = ImageFont.load_default()
        font_small = font
    
    # Draw accent bar at top
    draw.rectangle([(0, 0), (WIDTH, 20)], fill=ACCENT_COLOR)
    
    # Draw text centered
    y_start = HEIGHT // 3
    for i, line in enumerate(lines):
        if not line:
            continue
        # Use accent color for first line of each slide
        fill = ACCENT_COLOR if i == 0 else TEXT_COLOR
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (WIDTH - text_width) // 2
        draw.text((x, y_start + i * (font_size + 20)), line, font=font, fill=fill)
    
    # Draw accent bar at bottom
    draw.rectangle([(0, HEIGHT-20), (WIDTH, HEIGHT)], fill=ACCENT_COLOR)
    
    # Save slide
    filename = f"{OUTPUT_DIR}/slide{slide_num}.png"
    img.save(filename, "PNG")
    print(f"Created: {filename}")
    return filename

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for i, lines in enumerate(SLIDES, 1):
        create_slide(i, lines)
    
    print(f"\n✅ {len(SLIDES)} Slides erstellt in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
