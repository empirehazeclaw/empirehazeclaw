#!/bin/bash
# 🚀 EmpireHazeClaw AI Employee Kit - Deployment Script
# Usage: ./deploy_kit.sh --email kunde@example.com --agents email,support,analytics

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🦞 EmpireHazeClaw AI Employee Deployment${NC}"
echo "========================================"

# Parse arguments
CUSTOMER_EMAIL=""
AGENTS="email,support,analytics"
BRANCH="generic"

while [[ $# -gt 0 ]]; do
    case $1 in
        --email)
            CUSTOMER_EMAIL="$2"
            shift 2
            ;;
        --agents)
            AGENTS="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$CUSTOMER_EMAIL" ]; then
    echo -e "${RED}❌ Email is required: --email kunde@example.com${NC}"
    exit 1
fi

echo -e "${YELLOW}📧 Customer: $CUSTOMER_EMAIL${NC}"
echo -e "${YELLOW}🤖 Agents: $AGENTS${NC}"
echo ""

# Create installation directory
INSTALL_DIR="/opt/ai-employee"
echo -e "${GREEN}📁 Creating installation directory...${NC}"
sudo mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Clone or download kit
echo -e "${GREEN}📦 Downloading AI Employee Kit...${NC}"
# In production, this would pull from EmpireHazeClaw servers
# For now, we'll create the structure

sudo mkdir -p agents config data logs

# Create startup script
cat > $INSTALL_DIR/start.sh << 'STARTSCRIPT'
#!/bin/bash
# Start all AI Employee agents

echo "🦞 Starting AI Employee agents..."

for agent in agents/*.py; do
    if [ -f "$agent" ]; then
        name=$(basename $agent .py)
        echo "Starting $name..."
        nohup python3 $agent >> logs/$name.log 2>&1 &
    fi
done

echo "✅ All agents started!"
STARTSCRIPT

chmod +x $INSTALL_DIR/start.sh

# Create cron job for periodic execution
echo -e "${GREEN}⏰ Setting up cron jobs...${NC}"
(crontab -l 2>/dev/null || true; echo "*/15 * * * * cd $INSTALL_DIR && python3 agents/email_agent.py >> logs/email.log 2>&1") | crontab -

# Create systemd service
echo -e "${GREEN}🔧 Creating systemd service...${NC}"
sudo tee /etc/systemd/system/ai-employee.service > /dev/null << SERVICE
[Unit]
Description=EmpireHazeClaw AI Employee
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/bin/bash $INSTALL_DIR/start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl enable ai-employee
sudo systemctl start ai-employee

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo "========================================"
echo -e "${GREEN}📧 Customer: $CUSTOMER_EMAIL${NC}"
echo -e "${GREEN}📁 Install: $INSTALL_DIR${NC}"
echo -e "${GREEN}🤖 Agents: $AGENTS${NC}"
echo ""
echo -e "Next steps:"
echo "1. Configure agents: nano $INSTALL_DIR/config/"
echo "2. Add customer data: $INSTALL_DIR/data/"
echo "3. Set cron schedule as needed"
echo ""
