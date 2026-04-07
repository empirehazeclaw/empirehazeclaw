#!/usr/bin/env python3
"""Edge TTS Voice Messages"""
import subprocess
import sys
import os

AVAILABLE_VOICES = {
    "de": "de-DE-SeraphinaMultilingualNeural",
    "en": "en-US-AriaNeural",
    "en-uk": "en-GB-SoniaNeural"
}

def speak(text, voice="de-DE-SeraphinaMultilingualNeural", output="voice.mp3"):
    """Convert text to speech"""
    cmd = ["edge-tts", "--voice", voice, "--text", text, "--write-file", output]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return f"✅ Saved: {output}" if result.returncode == 0 else f"❌ {result.stderr}"

def list_voices():
    """List available voices"""
    return AVAILABLE_VOICES

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "Hallo!"
    output = sys.argv[2] if len(sys.argv) > 2 else "voice.mp3"
    print(f"=== 🎤 EDGE-TTS ===")
    print(speak(text, output=output))
