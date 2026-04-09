#!/bin/bash
# Ollama Warmup - Hält Modelle im RAM, alertet bei Fehlern

echo "🔥 Warming up Ollama..."

# Warm up qwen model
result=$(curl -s http://127.0.0.1:11434/api/generate -d '{"model":"qwen2.5:3b","prompt":"ready","options":{"num_predict":1}}' 2>&1)

if echo "$result" | grep -q "error"; then
    echo "⚠️ Ollama Error: $result"
    # Could send alert here
    exit 1
else
    echo "✅ Ollama ready!"
    exit 0
fi
