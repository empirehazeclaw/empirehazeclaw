#!/usr/bin/env python3
"""
Schnelle Whisper Transkription - nutzt tiny model für Speed.
Usage: python3 transcribe.py <audio_file>
"""
import sys
from faster_whisper import WhisperModel

# Model laden (einmalig)
model = WhisperModel("tiny", device="cpu", compute_type="int8")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 transcribe.py <audio_file>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    segments, _ = model.transcribe(audio_path, language="de")
    text = "".join([seg.text for seg in segments])
    print(text)
