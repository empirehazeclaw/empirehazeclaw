#!/bin/bash
# Edge TTS Wrapper — Sir HazeClaw
# Usage: edge-tts-wrapper.sh "Text to speak" [voice]
# Voice default: de-DE-SeraphinaMultilingualNeural

TEXT="${1:-}"
VOICE="${2:-de-DE-SeraphinaMultilingualNeural}"
OUTPUT="${3:-}"

if [ -z "$TEXT" ]; then
    echo "Usage: edge-tts-wrapper.sh \"Text\" [voice] [output_file]"
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    OUTPUT="/tmp/edge_tts_$(date +%Y%m%d_%H%M%S).mp3"
fi

edge-tts -t "$TEXT" -v "$VOICE" --write-media "$OUTPUT" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Saved: $OUTPUT"
    echo "Size: $(ls -lh "$OUTPUT" | awk '{print $5}')"
else
    echo "❌ Failed"
    exit 1
fi