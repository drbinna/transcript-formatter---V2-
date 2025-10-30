FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    ca-certificates \
    curl \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ /app/backend/

# Build frontend
COPY frontend/ /app/frontend/
RUN cd /app/frontend && npm install && npm run build

# Expose port
EXPOSE 8000

# Set working directory to backend
WORKDIR /app/backend

# Conservative pacing defaults for hosted envs; override in Render env vars if desired
ENV CHUNK_SLEEP_SECONDS=3 \
    RUN_COOLDOWN_SECONDS=30

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

