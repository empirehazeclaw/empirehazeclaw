#!/bin/bash
# SIR HAZECLAW Episode Creator
# Usage: ./make-sir-hazeclaw.sh "story text"

STORY="${1:-Sir Hazeclaw was once a great knight. But in the digital age, he is lost. His sword battery is empty. Now he must find a charging station!}"
OUTPUT="/var/www/empirehazeclaw-de/EPISODE_SIR_HAZECLAW.mp4"

echo "Creating SIR HAZECLAW episode..."
echo "Story: $STORY"

node /home/clawbot/.openclaw/workspace/scripts/sir-hazeclaw-pipeline.js "$STORY"
