#!/bin/bash
set -e

# Co-Op OS One-Click Installer (Linux/macOS)
# -----------------------------------------

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Co-Op Autonomous Company OS Installer...${NC}"

# 1. Dependency Checks
echo -e "\n🔍 Checking dependencies..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed.${NC}"
    echo "Please install Docker Desktop (macOS) or Docker Engine (Linux) and try again."
    exit 1
else
    echo -e "${GREEN}✅ Docker found: $(docker --version)${NC}"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ $(echo "$PYTHON_VERSION < 3.10" | bc -l) -eq 1 ]]; then
    echo -e "${RED}❌ Python 3.10 or higher is required. Found: $PYTHON_VERSION${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Python found: $PYTHON_VERSION${NC}"
fi

# 2. Install CLI
echo -e "\n🛠️ Installing Co-Op CLI..."
pip3 install -e ./cli

# 3. Onboarding
echo -e "\n🌟 Starting Onboarding Wizard..."
coop onboard setup

# 4. Service Setup (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "\n🐧 Setting up systemd service..."
    SERVICE_PATH="/etc/systemd/system/coop.service"
    USER_NAME=$(whoami)
    WORKING_DIR=$(pwd)
    
    cat <<EOF | sudo tee $SERVICE_PATH > /dev/null
[Unit]
Description=Co-Op Autonomous Company OS
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=$USER_NAME
WorkingDirectory=$WORKING_DIR
ExecStart=/usr/local/bin/coop gateway start
ExecStop=/usr/local/bin/coop gateway stop

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable coop.service
    echo -e "${GREEN}✅ Systemd service installed and enabled.${NC}"
fi

echo -e "\n${GREEN}✨ Installation Complete! ✨${NC}"
echo -e "You can now run ${BLUE}coop gateway start${NC} to launch the system."
