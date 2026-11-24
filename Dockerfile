# =============================================================================
# TechNova AI Sales Assistant - Production Docker Container
# =============================================================================
# Multi-stage lightweight container with volume-backed persistent storage
# for SQLite database and ChromaDB vector collections.
# =============================================================================

FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Container Storage Directory for persistent SQLite and ChromaDB volumes
ENV STORAGE_DIR=/app/storage

WORKDIR /app

# Install system dependencies required for building C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ /app/app/
COPY data/ /app/data/
COPY frontend/ /app/frontend/
COPY scripts/ /app/scripts/
COPY tests/ /app/tests/
COPY run_app.py /app/

# Declare persistent storage volume
VOLUME ["/app/storage"]

# Expose FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Run Unified Stack (FastAPI + Streamlit with auto-seed on first volume mount)
CMD ["python", "run_app.py"]
