#!/usr/bin/env python3
"""
🎬 TikTok Video Generator
Nutzt Pika Labs oder Runway für AI-Videos

Usage:
  python3 scripts/tiktok_video.py --image path/to/image.png --prompt "bewege das Bild"
  python3 scripts/tiktok_video.py --text "dein Text" --style "tech"
"""

import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser(description='🎬 TikTok AI Video Generator')
    parser.add_argument('--image', '-i', help='Pfad zum Bild')
    parser.add_argument('--prompt', '-p', help='Bewegungs-Prompt für Pika')
    parser.add_argument('--text', '-t', help='Text für Video')
    parser.add_argument('--style', '-s', default='cinematic', help='Stil: cinematic, animated, tech')
    parser.add_argument('--tool', default='pika', choices=['pika', 'runway'], help='Welches Tool')
    
    args = parser.parse_args()
    
    print("🎬 TikTok Video Generator")
    print("=" * 40)
    
    if args.tool == 'pika':
        print("\n📌 Pika Labs wird verwendet.")
        print("\n⚡ Quick Start:")
        print("   1. Gehe auf: https://pika.art")
        print("   2. Logge dich ein (kostenlos)")
        print("   3. Lade dein Bild hoch")
        
        if args.prompt:
            print(f"   4. Prompt: {args.prompt}")
        if args.image:
            print(f"   5. Bild: {args.image}")
        
        print("\n🎁 Kostenlos: 30 Credits/Monat")
        print("📱 Unterstützte Formate: MP4, GIF")
        
    elif args.tool == 'runway':
        print("\n📌 Runway Gen-2 wird verwendet.")
        print("\n⚡ Quick Start:")
        print("   1. Gehe auf: https://runwayml.com")
        print("   2. Erstelle Account")
        print("   3. Wähle Gen-2 → Text/Bild → Video")
        
        print("\n🎁 Kostenlos: 125 Credits/Monat")

    print("\n" + "=" * 40)
    print("💡 Tipp: Mehrere Accounts = mehr kostenlose Videos!")
    print("   z.B. 3 Accounts = 90 Credits/Monat")

if __name__ == '__main__':
    main()
