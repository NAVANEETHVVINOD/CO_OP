#!/bin/bash
set -e

# Co-Op OS One-Click Installer (Linux/macOS)
# -----------------------------------------

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Configurable variables via environment
INSTALL_DIR="${COOP_INSTALL_DIR:-$HOME/.co-op}"
COMPOSE_URL="${COOP_COMPOSE_URL:-https://raw.githubusercontent.com/NAVANEETHVVINOD/CO_OP/main/infrastructure/docker/docker-compose.yml}"
ENV_EXAMPLE_URL="${COOP_ENV_EXAMPLE_URL:-https://raw.githubusercontent.com/NAVANEETHVVINOD/CO_OP/main/infrastructure/docker/.env.example}"

echo -e "${BLUE}Starting Co-Op Autonomous Company OS Installer...${NC}"
echo -e "Install directory: ${BLUE}$INSTALL_DIR${NC}"
echo ""

# 1. Dependency Checks
echo -e "Checking dependencies..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker is not installed.${NC}"
    echo "Please install Docker Desktop (macOS) or Docker Engine (Linux) and try again."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
else
    echo -e "${GREEN}SUCCESS: Docker found: $(docker --version)${NC}"
fi

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}ERROR: Docker Compose is not installed or not available.${NC}"
    echo "Please ensure Docker Compose is installed and try again."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
else
    echo -e "${GREEN}SUCCESS: Docker Compose found: $(docker compose version)${NC}"
fi

# Check curl for downloading files
if ! command -v curl &> /dev/null; then
    echo -e "${RED}ERROR: curl is not installed.${NC}"
    echo "Please install curl and try again."
    exit 1
fi

# 2. Create installation directory
echo -e "\nCreating installation directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"
echo -e "${GREEN}SUCCESS: Installation directory created: $INSTALL_DIR${NC}"

# 3. Download configuration files
echo -e "\nDownloading configuration files..."

echo "Downloading docker-compose.yml..."
if curl -fsSL "$COMPOSE_URL" -o docker-compose.yml; then
    echo -e "${GREEN}SUCCESS: docker-compose.yml downloaded${NC}"
else
    echo -e "${RED}ERROR: Failed to download docker-compose.yml${NC}"
    exit 1
fi

echo "Downloading .env.example..."
if curl -fsSL "$ENV_EXAMPLE_URL" -o .env.example; then
    echo -e "${GREEN}SUCCESS: .env.example downloaded${NC}"
else
    echo -e "${RED}ERROR: Failed to download .env.example${NC}"
    exit 1
fi

# 4. Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "\nCreating .env file from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}SUCCESS: .env file created${NC}"
    echo ""
    echo -e "${YELLOW}IMPORTANT: You must edit the .env file before starting services!${NC}"
    echo -e "${YELLOW}   Edit: $INSTALL_DIR/.env${NC}"
    echo -e "${YELLOW}   Set your passwords, API keys, and other configuration values.${NC}"
    echo ""
else
    echo -e "\n${GREEN}SUCCESS: .env file already exists${NC}"
fi

# 5. Installation complete
echo -e "\n${GREEN}Installation Complete!${NC}"
echo ""
echo "Next steps:"
echo -e "  1. ${BLUE}Edit your configuration:${NC} $INSTALL_DIR/.env"
echo -e "  2. ${BLUE}Start the services:${NC} cd $INSTALL_DIR && docker compose up -d"
echo -e "  3. ${BLUE}Access the UI:${NC} http://localhost:3000"
echo ""
echo "For more information, visit: https://github.com/NAVANEETHVVINOD/CO_OP"
echo ""
