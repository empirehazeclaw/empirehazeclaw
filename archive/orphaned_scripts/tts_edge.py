#!/usr/bin/env python3
"""Edge-TTS - Better quality German voice"""

import asyncio
import os
import sys

def tts(text, lang="de"):
    voices = {
        "de": "de-DE-SeraphinaMultilingualNeural",
        "en": "en-US-JennyNeural"
    }
    voice = voices.get(lang, voices["de"])
    
    output = f"/tmp/tts_{os.getpid()}.mp3"
    
    async def speak():
        from edge_tts import Communicate
        communicate = Communicate(text, voice)
        await communicate.save(output)
    
    asyncio.run(speak())
    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: edge_tts.py \"Text to speak\" [de|en]")
        sys.exit(1)
    
    text = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "de"
    
    file = tts(text, lang)
    print(file)
