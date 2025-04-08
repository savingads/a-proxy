#!/bin/bash

# Start the A-Proxy development server

echo "Starting A-Proxy Development Server..."

# Check if a port was specified
PORT=${1:-5002}

# Activate the virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found."
    echo "Please run setup-dev-environment.sh first to create the virtual environment."
    exit 1
fi

# Start the application on the specified port
echo "Starting A-Proxy on port $PORT..."
python app.py --port $PORT

# This line will only be reached if the application exits
echo "A-Proxy has stopped."
