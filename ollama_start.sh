#!/bin/bash
# Ollama Auto-Start Script

if pgrep -x "ollama" > /dev/null; then
    echo "Ollama läuft bereits"
else
    echo "Starte Ollama..."
    nohup /usr/local/bin/ollama serve > /home/clawbot/.openclaw/logs/ollama.log 2>&1 &
    sleep 3
    echo "Ollama gestartet"
fi
