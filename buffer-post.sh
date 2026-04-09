#!/bin/bash
# 📱 Buffer Auto-Post Script
# Nutzt Buffer API für Social Media Posting

BUFFER_API_KEY="${BUFFER_ACCESS_TOKEN}"
PROFILE_ID="${BUFFER_PROFILE_ID}"

if [[ -z "$BUFFER_API_KEY" ]]; then
    echo "❌ Buffer API Key nicht konfiguriert"
    exit 1
fi

post_to_buffer() {
    local text="$1"
    local media="$2"
    
    curl -s -X POST "https://api.bufferapp.com/1/updates/create.json" \
        -d "api_key=$BUFFER_API_KEY" \
        -d "profile_ids[]=$PROFILE_ID" \
        -d "text=$text" \
        ${media:+"-d media=$media"} \
        | jq -r '.success // .message'
}

# Beispiel-Post
post_to_buffer "🚀 Managed AI Hosting - KI-Mitarbeiter für Ihr Unternehmen! #AI #ManagedHosting #Deutschland"

echo "✅ Buffer Post gesendet!"
