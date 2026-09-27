# =============================================================================
# FutureLens - production container
#
# Multi-stage build:
#   Stage 1 (node)   : build the Vite frontend into static assets
#   Stage 2 (python) : install the backend, copy the built frontend,
#                      and serve both from a single container
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1 - frontend build
# -----------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Output: /frontend/dist contains the production static files.


# -----------------------------------------------------------------------------
# Stage 2 - backend + static serving
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
        tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[swiss,gemini]"

COPY ephe/ ./ephe/
COPY app/ ./app/
COPY rulebook/ ./rulebook/

COPY --from=frontend-builder /frontend/dist ./frontend/dist

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health').read()" || exit 1

COPY docker/start.sh /app/docker/start.sh
RUN chmod +x /app/docker/start.sh

CMD ["/app/docker/start.sh"]
