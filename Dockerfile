# Use official lightweight Python image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application codebase
COPY app/ /app/app/
COPY data/ /app/data/
COPY frontend/ /app/frontend/
COPY scripts/ /app/scripts/
COPY tests/ /app/tests/
COPY .env.example /app/.env
COPY run_app.py /app/

# Pre-seed SQLite database and ChromaDB vector index
RUN python scripts/seed_db.py

# Expose FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Run Unified Stack
CMD ["python", "run_app.py"]
