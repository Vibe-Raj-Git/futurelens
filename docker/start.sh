#!/usr/bin/env bash
# =============================================================================
# FutureLens container entry point.
#
# Starts uvicorn on $PORT (default 8000). Uvicorn serves both the
# FastAPI app and the built frontend static files.
# =============================================================================

set -e

PORT="${PORT:-8000}"

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --proxy-headers \
    --forwarded-allow-ips="*" \
    --log-level info
