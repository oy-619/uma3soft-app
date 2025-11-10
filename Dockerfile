# Multi-stage build for size optimization
FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /build

# Copy requirements
COPY requirements.railway.txt /build/

# Install dependencies with optimization
RUN pip install --no-cache-dir --user -r requirements.railway.txt

# Final stage - minimal image
FROM python:3.12-slim

# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local

# Set work directory
WORKDIR /app

# Copy only necessary application files
COPY src/ /app/src/
COPY .env* /app/
COPY Procfile /app/

# Create required directories
RUN mkdir -p /tmp/chroma_store /tmp/conversation_history

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8080

# Run application
CMD ["python", "src/uma3.py"]
