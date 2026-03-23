FROM python:3.12-slim

# Install system dependencies (including supervisor for multi-process)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    procps \
    libpq-dev \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY pyproject.toml .

# Install core dependencies for model pre-downloading
RUN uv venv && \
    uv pip install torch --index-url https://download.pytorch.org/whl/cpu && \
    uv pip install sentence-transformers>=2.6.1

# Pre-download models (CACHED)
# This layer is independent of application changes, saving gigabytes of bandwidth and minutes of build time
RUN .venv/bin/python -c "\
from sentence_transformers import SentenceTransformer, CrossEncoder; \
print('Downloading all-MiniLM-L6-v2...'); \
SentenceTransformer('all-MiniLM-L6-v2'); \
print('Downloading ms-marco-MiniLM-L-6-v2...'); \
CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2'); \
print('SUCCESS')"

# Install full project dependencies from pyproject.toml
RUN uv pip install .

# Copy application code
COPY app ./app

# Copy process management config
COPY supervisord.conf /app/supervisord.conf
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Healthcheck that corresponds to the one in docker-compose
HEALTHCHECK --interval=30s --timeout=10s --retries=5 --start-period=60s \
    CMD curl -f http://localhost:8000/health || exit 1

# Run supervisord (manages uvicorn + arq worker)
CMD ["/app/entrypoint.sh"]
