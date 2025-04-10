#!/bin/bash

# A-Proxy Demo Runner Script
# This script simplifies running the A-Proxy demonstration

# Navigate to the demo directory
cd "$(dirname "$0")"

# Check if A-Proxy is running
echo "Checking if A-Proxy is running at http://localhost:5002..."
if ! curl -s --head http://localhost:5002 | head -1 | grep "HTTP/1.[01] [23].." > /dev/null; then
    echo "A-Proxy doesn't seem to be running."
    echo "Would you like to start it? (y/n)"
    read -r start_proxy
    
    if [[ $start_proxy == "y" || $start_proxy == "Y" ]]; then
        echo "Starting A-Proxy..."
        # Check if start-a-proxy.sh exists and is executable in parent directory
        if [ -x "../start-a-proxy.sh" ]; then
            # Run in background
            cd .. && ./start-a-proxy.sh &
            cd - > /dev/null
            # Store the PID
            PROXY_PID=$!
            echo "A-Proxy starting with PID: $PROXY_PID"
            # Wait for it to start
            echo "Waiting for A-Proxy to start..."
            sleep 10
        else
            echo "Trying to start with Python..."
            # Try to use Python directly
            if [ -d "../venv" ]; then
                cd .. && ./venv/bin/python app.py &
                cd - > /dev/null
                PROXY_PID=$!
                echo "A-Proxy starting with PID: $PROXY_PID"
                echo "Waiting for A-Proxy to start..."
                sleep 10
            else
                echo "Could not find a way to start A-Proxy"
                echo "Please start A-Proxy manually and run this script again."
                exit 1
            fi
        fi
    else
        echo "Please start A-Proxy manually and run this script again."
        exit 1
    fi
fi

# Check if dependencies are installed
echo "Checking dependencies..."
if ! npm list puppeteer puppeteer-screen-recorder > /dev/null 2>&1; then
    echo "Installing dependencies..."
    npm install
fi

# Create directories if they don't exist
mkdir -p screenshots videos

# Run the demo
echo "Starting A-Proxy feature demonstration..."
node demo-script.js

# If demo completed successfully, offer to generate PDF report
if [ $? -eq 0 ]; then
    echo "Demo completed successfully!"
    echo "Would you like to generate a PDF report of the demonstration? (y/n)"
    read -r gen_pdf
    
    if [[ $gen_pdf == "y" || $gen_pdf == "Y" ]]; then
        echo "Generating PDF report..."
        node create-pdf-report.js
        
        if [ $? -eq 0 ]; then
            echo "PDF report generated successfully: A-Proxy-Demo-Report.pdf"
        else
            echo "Error generating PDF report."
        fi
    fi
else
    echo "Demo did not complete successfully. Check the console output for errors."
fi

echo ""
echo "Screenshots saved to: ./screenshots"
echo "Video saved to: ./videos/a-proxy-demo.mp4"

# Offer to open the video
echo "Would you like to open the demo video? (y/n)"
read -r open_video

if [[ $open_video == "y" || $open_video == "Y" ]]; then
    if [ -f "./videos/a-proxy-demo.mp4" ]; then
        echo "Opening video..."
        # Try to open with appropriate command based on OS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            open "./videos/a-proxy-demo.mp4"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            xdg-open "./videos/a-proxy-demo.mp4"
        elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            # Windows
            start "./videos/a-proxy-demo.mp4"
        else
            echo "Could not determine how to open the video on your OS."
            echo "Please open it manually from: ./videos/a-proxy-demo.mp4"
        fi
    else
        echo "Video file not found. The demo may not have completed successfully."
    fi
fi

echo "Thank you for using the A-Proxy demonstration script!"
