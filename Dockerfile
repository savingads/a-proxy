FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    python3-dev \
    build-essential \
    pkg-config \
    libffi-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create directories for persistent data
RUN mkdir -p /app/data

# Copy requirements and install Python dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefer-binary -r requirements.txt

# Install Playwright Chromium browser and its system dependencies
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

# Create startup script
# Note: Database auto-initializes on first import via database/__init__.py
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "A-Proxy Container Starting..."\n\
\n\
# Wait for LLM endpoint if configured (gives Ollama time to pull the model)\n\
if [ -n "$OPENAI_COMPATIBLE_URL" ]; then\n\
    BASE_URL=$(echo "$OPENAI_COMPATIBLE_URL" | sed "s|/v1$||")\n\
    echo "Waiting for LLM endpoint at $BASE_URL ..."\n\
    for i in $(seq 1 60); do\n\
        if curl -sf "$BASE_URL/" > /dev/null 2>&1; then\n\
            echo "LLM endpoint is ready."\n\
            break\n\
        fi\n\
        if [ "$i" -eq 60 ]; then\n\
            echo "Warning: LLM endpoint not reachable after 60s. Starting anyway."\n\
        fi\n\
        sleep 2\n\
    done\n\
fi\n\
\n\
# Create sample personas if database is empty\n\
if [ ! -f "/app/data/personas.db" ]; then\n\
    echo "Creating sample personas..."\n\
    python /app/create_sample_personas_simple.py\n\
fi\n\
\n\
# Initialize default user (idempotent - skips if exists)\n\
echo "Checking default user..."\n\
python /app/init_default_user.py\n\
\n\
echo "Starting A-Proxy on port 5002..."\n\
exec python /app/app.py --host 0.0.0.0 --port 5002\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose the application port
EXPOSE 5002

# Define health check for container monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5002/ || exit 1

# Run the start script
CMD ["/app/start.sh"]
