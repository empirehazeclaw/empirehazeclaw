#!/usr/bin/env python3
"""
Fast Whisper Transcription — Sir HazeClaw
Uses faster-whisper with tiny model for ~2s transcription
"""
import sys
from faster_whisper import WhisperModel

if len(sys.argv) < 2:
    print("Usage: fast_whisper.py <audio-file>")
    sys.exit(1)

model = WhisperModel('tiny', device='cpu', compute_type='int8')
segments, _ = model.transcribe(sys.argv[1], language='de')
text = ''.join([s.text for s in list(segments)])
print(text)
