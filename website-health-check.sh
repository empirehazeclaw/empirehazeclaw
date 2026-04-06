#!/bin/bash
# 🌐 Website Health Check

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_site() {
    local url=$1
    local name=$2
    local secure=${3:-yes}
    
    if [[ "$secure" == "yes" ]]; then
        status=$(curl -skf -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")
    else
        status=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")
    fi
    
    case $status in
        200) echo -e "${GREEN}✅${NC} $name: OK" ;;
        301|302) echo -e "${YELLOW}⚠️${NC} $name: Redirect ($status)" ;;
        400|404) echo -e "${RED}❌${NC} $name: Not Found ($status)" ;;
        000) echo -e "${RED}❌${NC} $name: Down/Timeout" ;;
        *) echo -e "${YELLOW}⚠️${NC} $name: HTTP $status" ;;
    esac
}

echo "🌐 Website Health Check - $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

check_site "https://empirehazeclaw.com" "empirehazeclaw.com"
check_site "https://empirehazeclaw.de" "empirehazeclaw.de"
check_site "https://empirehazeclaw.store" "empirehazeclaw.store"
check_site "https://empirehazeclaw.info" "empirehazeclaw.info"
check_site "https://187.124.11.27:8889" "Mission Control"
