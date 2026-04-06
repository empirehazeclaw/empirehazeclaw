#!/bin/bash
# High-Quality TTS Wrapper für OpenClaw
# Nutzt zwingend Seraphina und umgeht das base64-Längenlimit von Telegram

TEXT="$1"
OUTPUT_FILE="/tmp/tts_$(date +%s).mp3"
TARGET_CHAT=${2:-"5392634979"}

if [ -z "$TEXT" ]; then
    echo "Usage: ./speak_high_quality.sh \"Dein Text\" [chat_id]"
    exit 1
fi

echo "🎤 Generiere Seraphina-Voice..."
node /home/clawbot/.openclaw/workspace/scripts/ttsnotify.js "$TEXT" --output "$OUTPUT_FILE"

if [ -f "$OUTPUT_FILE" ]; then
    echo "📲 Sende an Telegram via OpenClaw Message Tool..."
    openclaw message send --channel telegram --target "$TARGET_CHAT" --message "Voice Message:" --filePath "$OUTPUT_FILE" --asVoice
    echo "✅ Erfolgreich gesendet!"
else
    echo "❌ Fehler: MP3 konnte nicht erstellt werden."
fi
