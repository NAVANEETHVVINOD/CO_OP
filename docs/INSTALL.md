# 📥 Installation Guide

Welcome to the Co-Op Autonomous Company OS. This guide covers how to get the system running on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker & Docker Compose**: To run the backend services (Postgres, Redis, Qdrant, etc.).
- **Python 3.12+**: Required for the CLI.
- **Node.js 20+ & pnpm**: Required for the frontend and desktop app.
- **Git**: To clone the repository.

---

## 🚀 Quick Install (Recommended)

We provide one-click installation scripts that handle dependency checks and CLI setup automatically.

### Windows (PowerShell)
Open PowerShell as an administrator and run:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/navaneethvvinod/co_op/main/install.ps1'))
```
*Note: If you have the repo cloned locally, you can just run `.\install.ps1` from the root.*

### Linux & macOS (Bash)
Open your terminal and run:
```bash
curl -sSL https://raw.githubusercontent.com/navaneethvvinod/co_op/main/install.sh | bash
```
*Note: If you have the repo cloned locally, you can just run `./install.sh` from the root.*

---

## 🛠️ Manual Installation

If you prefer to set things up manually:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/navaneethvvinod/co_op.git
    cd co_op
    ```

2.  **Install the CLI**:
    ```bash
    cd cli
    pip install -e .
    ```

3.  **Run Onboarding**:
    ```bash
    coop onboard setup
    ```
    Follow the prompts to configure your environment.

4.  **Start the Gateway**:
    ```bash
    coop gateway start
    ```

5.  **Run the Frontend**:
    ```bash
    cd apps/web
    pnpm install
    pnpm dev
    ```
    Access the dashboard at `http://localhost:3000`.

---

## 🖥️ Desktop App

To build or run the native desktop application:

1.  Navigate to the desktop directory:
    ```bash
    cd apps/desktop
    ```
2.  Install dependencies:
    ```bash
    pnpm install
    ```
3.  Run in development mode:
    ```bash
    pnpm tauri dev
    ```
4.  Build for production:
    ```bash
    pnpm tauri build
    ```

---

## ❓ Troubleshooting

- **Docker not running**: Ensure the Docker daemon is active. Run `docker info` to check.
- **Port conflicts**: Co-Op uses ports `8000` (API), `3000` (Web), `5433` (DB), `6379` (Redis). Ensure these are free.
- **Ollama/LiteLLM**: If you want local LLMs, ensure Ollama is running (`ollama serve`) before starting the gateway.
