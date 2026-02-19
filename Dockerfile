# =============================================================================
# acidni-support — Python API with pre-built widget
# Widget JS is built locally and committed to widget/dist/
# =============================================================================
FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy API source (needed for pip install)
COPY pyproject.toml ./
COPY api/ ./api/

# Install Python deps
RUN pip install --no-cache-dir .

# Copy pre-built widget JS
COPY widget/dist ./widget/dist

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
