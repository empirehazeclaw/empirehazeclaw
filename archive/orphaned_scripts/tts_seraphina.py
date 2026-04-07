#!/usr/bin/env python3
"""
Seraphina TTS - Deutsche Sprachausgabe
Verwendung: python3 tts_seraphina.py "Dein Text hier"
"""

import edge_tts
import asyncio
import sys
import os
from datetime import datetime

VOICE = "de-DE-SeraphinaMultilingualNeural"
OUTPUT_DIR = "/home/clawbot/.openclaw/media/outbound"

async def speak(text, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"seraphina_{timestamp}.mp3"
    
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)
    
    return output_path

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tts_seraphina.py \"Your text here\"")
        text = input("Text eingeben: ")
    else:
        text = " ".join(sys.argv[1:])
    
    output = await speak(text)
    print(f"✅ Saved: {output}")
    return output

if __name__ == "__main__":
    asyncio.run(main())
