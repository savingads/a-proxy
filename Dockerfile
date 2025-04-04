FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    unzip \
    chromium \
    openvpn \
    nodejs \
    npm \
    python3-dev \
    build-essential \
    file \
    pkg-config \
    libffi-dev \
    libbz2-dev \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libreadline-dev \
    liblzma-dev \
    python3-tk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create directories for persistent data and VPN config
RUN mkdir -p /app/data /app/nordvpn/ovpn_udp /app/nordvpn/ovpn_tcp

# Copy requirements and install Python dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy package.json and install Node.js dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Create a startup script to initialize the database if it doesn't exist
RUN echo '#!/bin/bash\n\
if [ ! -f "/app/data/personas.db" ]; then\n\
    echo "Initializing database..."\n\
    python /app/database.py\n\
    python /app/create_sample_personas.py\n\
fi\n\
\n\
echo "Starting A-Proxy application..."\n\
python /app/app.py --host 0.0.0.0 --port 5002\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose the application port
EXPOSE 5002

# Define health check for container monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5002/ || exit 1

# Run the start script
CMD ["/app/start.sh"]
