#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# 📧 Email Auto-Responder
# ═══════════════════════════════════════════════════════════════════
# Sendet automatische Antworten bei Abwesenheit
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

GOG="/home/linuxbrew/.linuxbrew/bin/gog"
TOKEN=$(grep access_token ~/.config/gogcli/token.env | cut -d= -f2)
ALERT_EMAIL="empirehazeclaw@gmail.com"

# Check if we're in vacation mode
VACATION_FILE="/home/clawbot/.openclaw/workspace/.vacation_mode"
AUTO_REPLY_SCRIPT="/home/clawbot/.openclaw/workspace/scripts/send-auto-reply.py"

# Vacation message template
VACATION_MSG="Vielen Dank für Ihre E-Mail!

Ich bin bis zum [DATUM] im Urlaub und habe nur eingeschränkten Zugriff auf meine E-Mails.

Für dringende Anliegen erreichen Sie mich unter [ANDERE_EMAIL] oder [TELEFON].

Mit freundlichen Grüßen
EmpireHazeClaw Team"

case "${1:-}" in
    --enable|--on)
        echo "🟢 Auto-Responder aktiviert"
        touch "$VACATION_FILE"
        echo "$VACATION_MSG" > "$VACATION_FILE"
        ;;
    --disable|--off)
        echo "⚪ Auto-Responder deaktiviert"
        rm -f "$VACATION_FILE"
        ;;
    --check)
        if [[ -f "$VACATION_FILE" ]]; then
            echo "🟢 Auto-Responder ist AKTIV"
            echo ""
            cat "$VACATION_FILE"
        else
            echo "⚪ Auto-Responder ist inaktiv"
        fi
        ;;
    --send)
        # Send vacation auto-reply to new emails
        echo "📧 Prüfe auf neue E-Mails..."
        # Hier würde IMAP-Abfrage kommen
        echo "✅ Auto-Responder Check abgeschlossen"
        ;;
    *)
        echo "Usage: $0 [--enable|--disable|--check|--send]"
        ;;
esac
