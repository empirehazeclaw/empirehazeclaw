#!/usr/bin/env python3
"""
Whisper Server - Hält das Model dauerhaft geladen für schnelle Transkription.
Nutzung: python3 whisper_server.py [audio_file]
"""
from faster_whisper import WhisperModel
import sys
import os

# Model einmal laden (beim Start)
print("[Whisper] Loading model...", file=sys.stderr)
model = WhisperModel("base", device="cpu", compute_type="int8")
print("[Whisper] Model geladen!", file=sys.stderr)

def transcribe(audio_path):
    """Transkribiere Audio-Datei"""
    segments, _ = model.transcribe(audio_path, language="de")
    text = " ".join([seg.text for seg in segments])
    return text

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 whisper_server.py <audio_file>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    if not os.path.exists(audio_path):
        print(f"File not found: {audio_path}")
        sys.exit(1)
    
    result = transcribe(audio_path)
    print(result)
