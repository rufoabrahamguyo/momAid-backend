# Stage 1: Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create venv and install requirements
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

# Stage 2: Final Run stage
FROM python:3.12-slim

WORKDIR /app

# Install ONLY the runtime libraries (e.g., libpq for Postgres)
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy the venv from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Ensure the venv is used
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

CMD ["sh", "start.sh"]
