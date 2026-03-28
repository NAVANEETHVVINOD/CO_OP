# Co-Op CLI

The Co-Op CLI (`coop`) is a command-line tool for managing the Co-Op Autonomous Company OS.

## Installation

```bash
pip install -e ./cli
```

## Commands

### Gateway Management

Manage the Docker stack that runs Co-Op services.

- `coop gateway start` - Start all Co-Op services using Docker Compose
- `coop gateway stop` - Stop all Co-Op services
- `coop gateway status` - Check status of services and API health
  - `--json` - Output status in JSON format for machine reading

### System Diagnostics

- `coop doctor check` - Run full system diagnostics (Docker, resources, environment, API)

### Backup

- `coop backup create` - Create a full system backup (Postgres, Qdrant, MinIO)

### Approvals

- `coop approve` - Approve pending actions (coming soon)

### Testing

- `coop test` - Run E2E verification suite (coming soon)

## Configuration

The CLI can be configured using environment variables to customize paths and settings.

### Environment Variables

#### COOP_COMPOSE_PATH

Path to the docker-compose.yml file.

- **Default:** `../infrastructure/docker/docker-compose.yml` (relative to CLI installation)
- **Example:** 
  ```bash
  export COOP_COMPOSE_PATH=/path/to/custom/docker-compose.yml
  coop gateway start
  ```

#### COOP_ENV_FILE

Path to the .env file used by Docker Compose.

- **Default:** `../infrastructure/docker/.env` (relative to CLI installation)
- **Example:**
  ```bash
  export COOP_ENV_FILE=/path/to/custom/.env
  coop gateway start
  ```

#### COOP_API_URL

URL of the Co-Op API backend.

- **Default:** `http://localhost:8000`
- **Example:**
  ```bash
  export COOP_API_URL=http://192.168.1.100:8000
  coop gateway status
  coop doctor check
  ```

### Setting Environment Variables

#### Linux & macOS

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export COOP_COMPOSE_PATH=/path/to/docker-compose.yml
export COOP_ENV_FILE=/path/to/.env
export COOP_API_URL=http://localhost:8000
```

Or set temporarily for a single command:

```bash
COOP_API_URL=http://192.168.1.100:8000 coop gateway status
```

#### Windows (PowerShell)

Set permanently:

```powershell
[System.Environment]::SetEnvironmentVariable('COOP_COMPOSE_PATH', 'C:\path\to\docker-compose.yml', 'User')
[System.Environment]::SetEnvironmentVariable('COOP_ENV_FILE', 'C:\path\to\.env', 'User')
[System.Environment]::SetEnvironmentVariable('COOP_API_URL', 'http://localhost:8000', 'User')
```

Or set temporarily for current session:

```powershell
$env:COOP_API_URL = "http://192.168.1.100:8000"
coop gateway status
```

#### Windows (Command Prompt)

Set permanently:

```cmd
setx COOP_COMPOSE_PATH "C:\path\to\docker-compose.yml"
setx COOP_ENV_FILE "C:\path\to\.env"
setx COOP_API_URL "http://localhost:8000"
```

Or set temporarily for current session:

```cmd
set COOP_API_URL=http://192.168.1.100:8000
coop gateway status
```

## Error Messages

The CLI provides clear error messages when configuration is missing or incorrect:

### Missing Compose File

```
ERROR: Compose file not found: /path/to/docker-compose.yml
Set COOP_COMPOSE_PATH environment variable to override
```

### Missing .env File

```
WARNING: .env file not found: /path/to/.env
Set COOP_ENV_FILE environment variable to override
```

### API Unreachable

```
ERROR: API is unreachable: Connection refused
```

When the API is unreachable, check:
1. Services are running: `coop gateway status`
2. API URL is correct: `echo $COOP_API_URL`
3. Firewall allows connections to the API port

## Common Workflows

### Initial Setup

```bash
# 1. Install CLI
pip install -e ./cli

# 2. Start services
coop gateway start

# 3. Check status
coop gateway status

# 4. Run diagnostics
coop doctor check
```

### Daily Operations

```bash
# Check system health
coop gateway status

# View service logs
docker compose -f $COOP_COMPOSE_PATH logs -f

# Restart a specific service
docker compose -f $COOP_COMPOSE_PATH restart co-op-api

# Stop all services
coop gateway stop
```

### Backup and Restore

```bash
# Create backup
coop backup create

# Backup is saved to ./backups/ directory
# Restore manually:
# 1. Stop services: coop gateway stop
# 2. Restore database: cat backup.sql | docker exec -i docker-postgres-1 psql -U coop coop_os
# 3. Start services: coop gateway start
```

### Monitoring

```bash
# Check status with JSON output (for scripts)
coop gateway status --json

# Check API health
curl http://localhost:8000/health

# Check resource usage
docker stats
```

## Examples

### Custom Installation Directory

If you installed Co-Op in a custom location:

```bash
export COOP_COMPOSE_PATH=/opt/co-op/infrastructure/docker/docker-compose.yml
export COOP_ENV_FILE=/opt/co-op/infrastructure/docker/.env
coop gateway start
```

### Remote API Server

If the API is running on a different machine:

```bash
export COOP_API_URL=http://192.168.1.100:8000
coop gateway status
coop doctor check
```

### Multiple Environments

Use different .env files for different environments:

```bash
# Development
export COOP_ENV_FILE=./infrastructure/docker/.env.dev
coop gateway start

# Staging
export COOP_ENV_FILE=./infrastructure/docker/.env.staging
coop gateway start

# Production
export COOP_ENV_FILE=./infrastructure/docker/.env.prod
coop gateway start
```

### Automated Monitoring Script

```bash
#!/bin/bash
# monitor.sh - Check Co-Op status every 5 minutes

while true; do
    STATUS=$(coop gateway status --json)
    if echo "$STATUS" | jq -e '.api.healthy == false' > /dev/null; then
        echo "API is unhealthy! Sending alert..."
        # Send alert (email, Slack, etc.)
    fi
    sleep 300
done
```

## Development

### Project Structure

```
cli/
├── coop/
│   ├── commands/
│   │   ├── gateway.py    # Gateway management commands
│   │   ├── doctor.py     # System diagnostics
│   │   ├── backup.py     # Backup commands
│   │   ├── approve.py    # Approval commands
│   │   ├── onboard.py    # Onboarding wizard
│   │   └── test.py       # Testing commands
│   ├── main.py           # CLI entry point
│   └── __init__.py
├── tests/
│   └── test_cli.py       # CLI tests
├── pyproject.toml        # Package configuration
└── README.md             # This file
```

### Running Tests

```bash
cd cli
pytest
```

### Adding New Commands

1. Create a new file in `cli/coop/commands/`
2. Define a Typer app and commands
3. Import and register in `cli/coop/main.py`

Example:

```python
# cli/coop/commands/mycommand.py
import typer
from rich.console import Console

app = typer.Typer(help="My custom command")
console = Console()

@app.command()
def hello():
    """Say hello."""
    console.print("[bold green]Hello from Co-Op![/bold green]")
```

```python
# cli/coop/main.py
from coop.commands import mycommand

app.add_typer(mycommand.app, name="mycommand")
```

## Troubleshooting

### Command Not Found

If `coop` command is not found after installation:

1. Ensure the CLI is installed: `pip install -e ./cli`
2. Check your PATH includes the Python scripts directory
3. Try running with full path: `python -m coop.main`

### Permission Denied

If you get permission errors when starting services:

1. Ensure Docker daemon is running
2. Ensure your user is in the `docker` group (Linux)
3. Try with sudo (not recommended for production)

### Services Won't Start

If services fail to start:

1. Check Docker is running: `docker ps`
2. Check compose file exists: `ls -la $COOP_COMPOSE_PATH`
3. Check .env file exists: `ls -la $COOP_ENV_FILE`
4. Check logs: `docker compose -f $COOP_COMPOSE_PATH logs`
5. Run diagnostics: `coop doctor check`

## Support

For issues, questions, or contributions:

- GitHub Issues: https://github.com/NAVANEETHVVINOD/CO_OP/issues
- Documentation: https://github.com/NAVANEETHVVINOD/CO_OP/tree/main/docs
