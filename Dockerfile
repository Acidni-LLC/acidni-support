# =============================================================================
# acidni-support — Multi-stage Docker build
# Stage 1: Build widget JS, Stage 2: Python API
# =============================================================================

# ── Stage 1: Build widget ───────────────────────────────────────────────────
FROM node:20-alpine AS widget-builder
WORKDIR /widget
COPY widget/package.json widget/package-lock.json* ./
RUN npm ci --ignore-scripts 2>/dev/null || npm install
COPY widget/ .
RUN npm run build

# ── Stage 2: Python API ────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy API source
COPY api/ ./api/

# Copy built widget
COPY --from=widget-builder /widget/dist ./widget/dist

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
