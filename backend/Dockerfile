FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Prophet and pandas
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port (Railway uses $PORT env var)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/api/health')" || exit 1

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1
