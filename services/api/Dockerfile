# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools to patched versions (security fixes)
# CVE-2025-47273 (setuptools), CVE-2025-8869 (pip), CVE-2026-1703 (pip)
RUN pip install --no-cache-dir --upgrade 'pip>=26.0' 'setuptools>=78.1.1'

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create venv and install dependencies
# We separate torch and sentence-transformers to leverage caching
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN uv pip install torch --index-url https://download.pytorch.org/whl/cpu && \
    uv pip install sentence-transformers>=2.6.1 alembic>=1.13.1

COPY pyproject.toml .
COPY app ./app
RUN uv pip install pytest pytest-asyncio pytest-mock aiosqlite bcrypt==4.0.1 && \
    uv pip install .

# --- Stage 2: Final Runtime ---
FROM python:3.12-slim

WORKDIR /app

# Upgrade pip and setuptools in runtime image (security fixes)
# CVE-2025-47273 (setuptools), CVE-2025-8869 (pip), CVE-2026-1703 (pip)
RUN pip install --no-cache-dir --upgrade 'pip>=26.0' 'setuptools>=78.1.1'

# Install runtime dependencies ONLY
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY app ./app
COPY tests ./tests
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY supervisord.conf /app/supervisord.conf
COPY entrypoint.sh /app/entrypoint.sh

# Ensure entrypoint is executable
RUN chmod +x /app/entrypoint.sh

# Environment defaults
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=5 --start-period=60s \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
