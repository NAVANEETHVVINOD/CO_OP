# Co-Op OS Installation Guide

This guide explains how to install Co-Op OS using the automated installer scripts.

## Quick Start

### Windows (PowerShell)

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/NAVANEETHVVINOD/CO_OP/main/install.ps1'))
```

### Linux & macOS (Bash)

```bash
curl -sSL https://raw.githubusercontent.com/NAVANEETHVVINOD/CO_OP/main/install.sh | bash
```

## Prerequisites

Before running the installer, ensure you have the following installed:

### Required Dependencies

1. **Docker Desktop** (Windows/macOS) or **Docker Engine** (Linux)
   - Windows: [Install Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)
   - macOS: [Install Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
   - Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)

2. **Docker Compose**
   - Included with Docker Desktop
   - Linux: [Install Docker Compose](https://docs.docker.com/compose/install/)

3. **curl** (Linux/macOS only)
   - Usually pre-installed on most systems
   - If missing: `sudo apt-get install curl` (Ubuntu/Debian) or `brew install curl` (macOS)

## Configuration Options

The installer scripts support environment variables for customization:

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COOP_INSTALL_DIR` | Installation directory | `$HOME/.co-op` (Linux/macOS)<br>`$HOME\.co-op` (Windows) |
| `COOP_COMPOSE_URL` | URL to download docker-compose.yml | GitHub main branch |
| `COOP_ENV_EXAMPLE_URL` | URL to download .env.example | GitHub main branch |

### Custom Installation Directory

To install Co-Op OS in a custom directory:

**Linux/macOS:**
```bash
export COOP_INSTALL_DIR=/opt/co-op
curl -sSL https://raw.githubusercontent.com/NAVANEETHVVINOD/CO_OP/main/install.sh | bash
```

**Windows:**
```powershell
$env:COOP_INSTALL_DIR = "C:\co-op"
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/NAVANEETHVVINOD/CO_OP/main/install.ps1'))
```

### Custom Configuration URLs

To use custom configuration files (e.g., from a fork or specific branch):

**Linux/macOS:**
```bash
export COOP_COMPOSE_URL="https://raw.githubusercontent.com/YOUR_USERNAME/CO_OP/YOUR_BRANCH/infrastructure/docker/docker-compose.yml"
export COOP_ENV_EXAMPLE_URL="https://raw.githubusercontent.com/YOUR_USERNAME/CO_OP/YOUR_BRANCH/infrastructure/docker/.env.example"
curl -sSL https://raw.githubusercontent.com/NAVANEETHVVINOD/CO_OP/main/install.sh | bash
```

**Windows:**
```powershell
$env:COOP_COMPOSE_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/CO_OP/YOUR_BRANCH/infrastructure/docker/docker-compose.yml"
$env:COOP_ENV_EXAMPLE_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/CO_OP/YOUR_BRANCH/infrastructure/docker/.env.example"
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/NAVANEETHVVINOD/CO_OP/main/install.ps1'))
```

## What the Installer Does

The installer performs the following steps:

1. **Dependency Checks**
   - Verifies Docker is installed
   - Verifies Docker Compose is available
   - Verifies curl is installed (Linux/macOS only)

2. **Creates Installation Directory**
   - Creates the installation directory (default: `~/.co-op`)
   - Changes to the installation directory

3. **Downloads Configuration Files**
   - Downloads `docker-compose.yml` from GitHub
   - Downloads `.env.example` from GitHub

4. **Creates Environment File**
   - Copies `.env.example` to `.env` (if `.env` doesn't exist)
   - Displays warning to edit `.env` before starting services

## Post-Installation Steps

After the installer completes, follow these steps:

### 1. Edit Configuration

Edit the `.env` file in your installation directory:

**Linux/macOS:**
```bash
cd ~/.co-op
nano .env  # or use your preferred editor
```

**Windows:**
```powershell
cd $HOME\.co-op
notepad .env
```

**Required Configuration:**
- Set secure passwords for `DB_PASS`, `MINIO_ROOT_PASSWORD`, `SECRET_KEY`
- Configure service URLs if not using defaults
- Set API keys for optional features (Telegram, Groq, Gemini)

See the comments in `.env.example` for detailed descriptions of each variable.

### 2. Start Services

**Linux/macOS:**
```bash
cd ~/.co-op
docker compose up -d
```

**Windows:**
```powershell
cd $HOME\.co-op
docker compose up -d
```

### 3. Verify Installation

Check that all services are running:

```bash
docker compose ps
```

All services should show status as "Up" or "healthy".

### 4. Access the UI

Open your browser and navigate to:
- **Web UI:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Troubleshooting

### Docker Not Found

**Error:** `❌ Docker is not installed`

**Solution:** Install Docker Desktop (Windows/macOS) or Docker Engine (Linux) from the links in the Prerequisites section.

### Docker Compose Not Available

**Error:** `❌ Docker Compose is not installed or not available`

**Solution:** 
- Windows/macOS: Ensure Docker Desktop is running
- Linux: Install Docker Compose plugin: `sudo apt-get install docker-compose-plugin`

### Download Failed

**Error:** `❌ Failed to download docker-compose.yml` or `❌ Failed to download .env.example`

**Solution:**
- Check your internet connection
- Verify the URLs are accessible
- Try using custom URLs with `COOP_COMPOSE_URL` and `COOP_ENV_EXAMPLE_URL`

### Permission Denied

**Error:** Permission denied when creating directories or files

**Solution:**
- Linux/macOS: Ensure you have write permissions to the installation directory
- Windows: Run PowerShell as Administrator

### Services Won't Start

**Error:** Services fail to start after `docker compose up -d`

**Solution:**
1. Check Docker is running: `docker ps`
2. Review logs: `docker compose logs`
3. Verify `.env` file has all required variables set
4. Ensure ports 3000, 8000, 5432, 6379, 9000, 6333, 11434 are not in use

## Manual Installation

If you prefer to install manually without the installer script:

1. Clone the repository:
   ```bash
   git clone https://github.com/NAVANEETHVVINOD/CO_OP.git
   cd CO_OP
   ```

2. Copy environment file:
   ```bash
   cd infrastructure/docker
   cp .env.example .env
   ```

3. Edit `.env` with your configuration

4. Start services:
   ```bash
   docker compose up -d
   ```

## Uninstallation

To uninstall Co-Op OS:

1. Stop and remove services:
   ```bash
   cd ~/.co-op  # or your custom installation directory
   docker compose down -v
   ```

2. Remove installation directory:
   ```bash
   rm -rf ~/.co-op  # or your custom installation directory
   ```

## Next Steps

After installation, see:
- [Deployment Guide](DEPLOYMENT.md) - For production deployment
- [Project Structure](PROJECT_STRUCTURE.md) - Understanding the codebase
- [README](../README.md) - General project information

## Support

For issues or questions:
- GitHub Issues: https://github.com/NAVANEETHVVINOD/CO_OP/issues
- Documentation: https://github.com/NAVANEETHVVINOD/CO_OP/tree/main/docs
