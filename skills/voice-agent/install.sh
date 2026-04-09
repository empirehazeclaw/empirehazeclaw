#!/bin/bash
# Voice Agent - Installation Script
# Usage: ./install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VOICE_AGENT_DIR="$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🎤 Voice Agent Installation          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check for OpenClaw workspace
if [ ! -d "$HOME/.openclaw/workspace" ]; then
    echo -e "${RED}❌ OpenClaw workspace not found${NC}"
    echo -e "${YELLOW}💡 Install OpenClaw first: https://docs.openclaw.ai${NC}"
    exit 1
fi

echo -e "${GREEN}✅ OpenClaw workspace found${NC}"

# Copy skill to OpenClaw skills directory
SKILLS_DIR="$HOME/.openclaw/workspace/skills/voice-agent"
echo -e "${YELLOW}📦 Installing to: $SKILLS_DIR${NC}"

mkdir -p "$SKILLS_DIR"
cp -r "$VOICE_AGENT_DIR"/* "$SKILLS_DIR/"

# Make scripts executable
echo -e "${YELLOW}🔧 Making scripts executable...${NC}"
chmod +x "$SKILLS_DIR/bin"/*

echo -e "${GREEN}✅ Scripts installed${NC}"

# Check for Whisper.cpp
if [ ! -d "$HOME/.local/whisper.cpp" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Whisper.cpp not installed${NC}"
    echo -e "${BLUE}💡 Would you like to install it now? (y/n)${NC}"
    read -r INSTALL_WHISPER
    
    if [[ "$INSTALL_WHISPER" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}📥 Installing Whisper.cpp...${NC}"
        git clone https://github.com/ggerganov/whisper.cpp ~/.local/whisper.cpp
        cd ~/.local/whisper.cpp
        make -j4
        bash ./models/download-ggml-model.sh tiny
        echo -e "${GREEN}✅ Whisper.cpp installed${NC}"
    fi
else
    echo -e "${GREEN}✅ Whisper.cpp already installed${NC}"
fi

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo ""
    echo -e "${YELLOW}⚠️  FFmpeg not installed${NC}"
    echo -e "${BLUE}💡 Install with: sudo apt-get install -y ffmpeg${NC}"
else
    echo -e "${GREEN}✅ FFmpeg already installed${NC}"
fi

# Add to PATH
echo ""
echo -e "${YELLOW}📌 Adding to PATH...${NC}"
echo ""
echo "Add this to your ~/.bashrc or ~/.zshrc:"
echo ""
echo "  export PATH=\"\$HOME/.openclaw/workspace/skills/voice-agent/bin:\$PATH\""
echo ""

# Test installation
echo -e "${YELLOW}🧪 Testing installation...${NC}"

if [ -f "$SKILLS_DIR/bin/voice-to-text" ]; then
    echo -e "${GREEN}✅ voice-to-text: OK${NC}"
else
    echo -e "${RED}❌ voice-to-text: NOT FOUND${NC}"
fi

if [ -f "$SKILLS_DIR/bin/text-to-voice" ]; then
    echo -e "${GREEN}✅ text-to-voice: OK${NC}"
else
    echo -e "${RED}❌ text-to-voice: NOT FOUND${NC}"
fi

if [ -f "$SKILLS_DIR/bin/voice-agent" ]; then
    echo -e "${GREEN}✅ voice-agent: OK${NC}"
else
    echo -e "${RED}❌ voice-agent: NOT FOUND${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Installation Complete!             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📖 Next Steps:${NC}"
echo ""
echo "1. Add to PATH (if not done):"
echo "   export PATH=\"\$HOME/.openclaw/workspace/skills/voice-agent/bin:\$PATH\""
echo ""
echo "2. Test installation:"
echo "   voice-agent --help"
echo ""
echo "3. Start using voice commands:"
echo "   voice-agent \"Hello!\""
echo ""
echo -e "${YELLOW}📚 Documentation: $SKILLS_DIR/README.md${NC}"
echo ""
