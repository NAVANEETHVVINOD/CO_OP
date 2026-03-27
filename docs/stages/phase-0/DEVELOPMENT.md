# 🛠️ Development Guide

Thank you for contributing to Co-Op! This document will help you set up your development environment.

## 🏗️ Architecture Overview

Co-Op is a distributed system with several core components:

- **Frontend (`apps/web`)**: Next.js dashboard.
- **Desktop (`apps/desktop`)**: Tauri-based Rust wrapper.
- **Backend API (`services/api`)**: FastAPI control plane.
- **CLI (`cli/`)**: Python-based management tool.
- **Infrastructure**: Docker Compose manages Postgres, Redis, Qdrant, and MinIO.

---

## 💻 Local Development Setup

1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/navaneethvvinod/co_op.git
    cd co_op
    ```

2.  **Backend Development**:
    - Install dependencies: `cd services/api && pip install -e .[dev]`
    - Run migrations: `alembic upgrade head`
    - Run with reload: `uvicorn app.main:app --reload --port 8000`

3.  **Frontend Development**:
    - Install dependencies: `cd apps/web && pnpm install`
    - Run dev server: `pnpm dev`

4.  **CLI Development**:
    - Install in editable mode: `cd cli && pip install -e .`

---

## 🧪 Testing

We use `pytest` for backend tests and `coop test` for E2E verification.

- **Backend Unit Tests**:
  ```bash
  cd services/api
  pytest
  ```
- **E2E Gold Path**:
  ```bash
  coop test
  ```

---

## 📜 Coding Standards

- **Python**: We follow PEP8. Use `ruff` for linting and formatting.
- **TypeScript**: Use `pnpm lint` in the web and desktop directories.
- **Rust**: Use `cargo fmt` and `cargo clippy`.

---

## 🚀 Release Process

1.  Update the version in `services/api/pyproject.toml` and `apps/desktop/src-tauri/tauri.conf.json`.
2.  Update the `CHANGELOG.md` (if applicable).
3.  Tag the release: `git tag v1.0.0`.
4.  Push tags: `git push origin v1.0.0`.

The GitHub Actions workflow will automatically build release assets and publish them.
