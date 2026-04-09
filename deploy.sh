#!/bin/bash
# EmpireHazeClaw Quick Deploy Script
# Usage: ./deploy.sh [de|com|info|store|all]

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Config
SOURCE_DIR="/home/clawbot/.openclaw/workspace/websites"
TARGETS=(
    "de:/var/www/empirehazeclaw-de"
    "com:/var/www/empirehazeclaw-com"
    "info:/var/www/empirehazeclaw-info"
    "store:/var/www/empirehazeclaw-store"
)

echo -e "${GREEN}🚀 EmpireHazeClaw Deployment${NC}\n"

# Function to deploy single site
deploy_site() {
    local key=$1
    local target=$2
    
    echo -e "${YELLOW}Deploying to $key...${NC}"
    
    # Create target if not exists
    mkdir -p "$target"
    
    # Copy files (exclude hidden and temp files)
    rsync -av --delete \
        --exclude='.DS_Store' \
        --exclude='Thumbs.db' \
        --exclude='*.tmp' \
        --exclude='*.bak' \
        --exclude='node_modules/' \
        --exclude='.git/' \
        "$SOURCE_DIR/$key/" "$target/"
    
    echo -e "${GREEN}✅ $key deployed!${NC}"
}

# Parse arguments
TARGET="${1:-all}"

if [ "$TARGET" = "all" ]; then
    for entry in "${TARGETS[@]}"; do
        IFS=':' read -r key target <<< "$entry"
        deploy_site "$key" "$target"
    done
elif [ "$TARGET" = "status" ]; then
    echo "📊 Current Status:"
    for entry in "${TARGETS[@]}"; do
        IFS=':' read -r key target <<< "$entry"
        if [ -d "$target" ]; then
            count=$(find "$target" -type f -name "*.html" | wc -l)
            echo -e "  $key: ✅ $count HTML files"
        else
            echo -e "  $key: ❌ Not found"
        fi
    done
else
    found=false
    for entry in "${TARGETS[@]}"; do
        IFS=':' read -r key target <<< "$entry"
        if [ "$key" = "$TARGET" ]; then
            deploy_site "$key" "$target"
            found=true
            break
        fi
    done
    
    if [ "$found" = false ]; then
        echo -e "${RED}Unknown target: $TARGET${NC}"
        echo "Usage: ./deploy.sh [de|com|info|store|all|status]"
        exit 1
    fi
fi

echo -e "\n${GREEN}🎉 Deployment complete!${NC}"
