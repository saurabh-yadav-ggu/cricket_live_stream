# syntax=docker/dockerfile:1
# StreamBox - AWS Production Dockerfile
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install curl for AWS container health check probes
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for optimal Docker layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and assets
COPY main.py /app/main.py
COPY stream_sync.py /app/stream_sync.py
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY Sonyliv-Playlist-Autoupdate/ /app/Sonyliv-Playlist-Autoupdate/

# Create a non-privileged user for security compliance in cloud environments
RUN useradd -u 1001 -m -s /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose default HTTP port
EXPOSE 8000

# Container healthcheck for AWS ECS, App Runner, and Docker Compose
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Launch FastAPI with Uvicorn (2 workers optimal for I/O streaming proxy workloads)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
