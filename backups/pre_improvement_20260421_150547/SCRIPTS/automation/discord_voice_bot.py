#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Discord Voice Bot
====================================
Basic Voice Bot for Discord Voice Channels.

Features:
- Join/Leave Voice Channels
- Speech-to-Text with faster-whisper
- Text-to-Speech with edge-tts
- OpenClaw Integration

Usage:
    python3 discord_voice_bot.py
"""

import os
import sys
import asyncio
import wave
import json
from datetime import datetime
from pathlib import Path

import discord
from discord.ext import voice_recv

# Load bot token from environment
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not BOT_TOKEN or BOT_TOKEN == "DISCORD_BOT_TOKEN":
    print("ERROR: DISCORD_BOT_TOKEN not set in environment")
    sys.exit(1)

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
LOG_DIR = WORKSPACE.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "discord_voice.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

class WhisperSTT:
    """Fast Speech-to-Text using faster-whisper."""
    
    def __init__(self):
        log("Loading Whisper model...")
        from faster_whisper import WhisperModel
        self.model = WhisperModel('tiny', device='cpu', compute_type='int8')
        log("Whisper model loaded")
    
    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio bytes to text."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        try:
            segments, _ = self.model.transcribe(temp_path, language='de')
            text = ''.join([s.text for s in list(segments)])
            return text.strip()
        finally:
            os.unlink(temp_path)

class EdgeTTS:
    """Text-to-Speech using edge-tts."""
    
    def __init__(self):
        self.voice = "de-DE-SeraphinaMultilingualNeural"
    
    async def speak(self, text: str, output_path: str):
        """Generate TTS audio file."""
        import subprocess
        cmd = [
            "edge-tts",
            "-t", text,
            "-v", self.voice,
            "--write-media", output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

class VoiceBot(discord.Client):
    """Discord Voice Bot with Speech Recognition."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.messages = True
        super().__init__(intents=intents)
        
        self.stt = WhisperSTT()
        self.tts = EdgeTTS()
        self.voice_client = None
        self.current_channel = None
        
    async def on_ready(self):
        log(f"Bot logged in as {self.user}")
        log("Commands: !join <channel>, !leave, !transcribe")
        
    async def on_message(self, message):
        """Handle text commands."""
        if message.author.bot:
            return
        
        if message.content.startswith('!join'):
            # Extract channel name or join user's channel
            if len(message.content.split()) > 1:
                channel_name = ' '.join(message.content.split()[1:])
                channel = discord.utils.get(message.guild.voice_channels, name=channel_name)
            else:
                # Try to join the user's voice channel
                if message.author.voice:
                    channel = message.author.voice.channel
                else:
                    await message.channel.send("Du bist in keinem Voice Channel!")
                    return
            
            if channel:
                await channel.connect(cls=discord.VoiceClient)
                self.current_channel = channel
                await message.channel.send(f"Joined {channel.name}!")
                log(f"Joined voice channel: {channel.name}")
            else:
                await message.channel.send(f"Channel '{channel_name}' nicht gefunden!")
        
        elif message.content == '!leave':
            if self.voice_client:
                await self.voice_client.disconnect()
                await message.channel.send("Left voice channel!")
                log("Left voice channel")
        
        elif message.content == '!test':
            # Test TTS
            test_file = "/tmp/test_tts.mp3"
            async def test_tts():
                success = await self.tts.speak("Hallo! Ich bin Sir HazeClaw. Voice Bot funktioniert!", test_file)
                if success and os.path.exists(test_file):
                    await message.channel.send(file=discord.File(test_file))
            await test_tts()
            
        elif message.content == '!help':
            await message.channel.send("""
**Sir HazeClaw Voice Bot Commands:**

`!join [channel_name]` - Join a voice channel
`!leave` - Leave current voice channel
`!test` - Test TTS
`!help` - Show this help
            """)

async def main():
    bot = VoiceBot()
    await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
