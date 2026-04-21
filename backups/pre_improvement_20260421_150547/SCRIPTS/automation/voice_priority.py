#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Voice Priority Handler v2
=============================================
Keeps model loaded for fast subsequent transcriptions.

Usage:
    python3 voice_priority.py <audio_file>
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Check for cached model to avoid reload
_cached_model = None
_model_loaded = False

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def get_model():
    """Get or load the faster-whisper model."""
    global _cached_model, _model_loaded
    if _cached_model is None:
        log("Loading model...")
        from faster_whisper import WhisperModel
        _cached_model = WhisperModel('tiny', device='cpu', compute_type='int8')
        _model_loaded = True
        log("Model loaded")
    return _cached_model

def transcribe_fast(audio_file):
    """Transcribe with cached model."""
    model = get_model()
    start = datetime.now()
    segments, _ = model.transcribe(audio_file, language='de')
    text = ''.join([s.text for s in list(segments)])
    elapsed = (datetime.now() - start).total_seconds()
    log(f"Transcribed in {elapsed:.1f}s")
    return text

def main():
    if len(sys.argv) < 2:
        print("Usage: voice_priority.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    log(f"=== Voice Priority Handler v2 ===")
    log(f"File: {Path(audio_file).name}")
    
    # Check if model already loaded
    if _model_loaded:
        log("Using cached model (fast mode)")
    
    # IMMEDIATELY print acknowledgment (for user to see)
    print("\n🎤 Bin gleich bei dir! (Transkribiere...)\n")
    
    # Then transcribe
    text = transcribe_fast(audio_file)
    
    # Output clean result
    print(f"\n📝: {text.strip()}")
    
    return text.strip()

if __name__ == "__main__":
    main()
