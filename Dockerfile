# ── Builder stage ────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_CACHE=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-dev

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Create a non-root user with a real, writable home. `adduser --system` defaults
# to /nonexistent, which breaks edgartools (it mkdirs ~/.edgar at import time).
RUN addgroup --system app \
    && adduser --system --ingroup app --home /home/app app \
    && mkdir -p /home/app/.edgar \
    && chown -R app:app /home/app

ENV HOME=/home/app \
    EDGAR_LOCAL_DATA_DIR=/home/app/.edgar

WORKDIR /app

# Copy the virtualenv from builder
COPY --from=builder /app/.venv .venv

# Copy application source
COPY app.py config.py llm_provider.py ./
COPY src/ src/

USER app

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
