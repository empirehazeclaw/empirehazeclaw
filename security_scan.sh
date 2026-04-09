#!/bin/bash
# Security Scan Wrapper - Lynis & RKHunter
# Nutzung: sudo bash security_scan.sh

echo "🛡️ Starte Security Scan..."
echo "=============================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Bitte als root ausführen: sudo bash security_scan.sh"
    exit 1
fi

echo ""
echo "📊 [1/3] System Info..."
uname -a
echo ""

echo "📊 [2/3] Lynis Security Scan..."
if command -v lynis &> /dev/null; then
    lynis audit system --quiet
else
    echo "⚠️ Lynis nicht installiert"
    echo "   Installieren mit: apt-get install lynis"
fi
echo ""

echo "📊 [3/3] RKHunter Scan..."
if command -v rkhunter &> /dev/null; then
    rkhunter --check --skip-keypress --report-warnings-only
else
    echo "⚠️ RKHunter nicht installiert"
    echo "   Installieren mit: apt-get install rkhunter"
fi
echo ""

echo "=============================="
echo "✅ Security Scan abgeschlossen!"
echo ""
echo "📝 Logs unter:"
echo "   - Lynis: /var/log/lynis.log"
echo "   - RKHunter: /var/log/rkhunter.log"
