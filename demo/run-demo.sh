#!/bin/bash

# A-Proxy Demo Runner Script
cd "$(dirname "$0")"

# Check if A-Proxy is running
echo "Checking if A-Proxy is running at http://localhost:5002..."
if ! curl -s --head http://localhost:5002 | head -1 | grep "HTTP/1.[01] [23].." > /dev/null; then
    echo "A-Proxy doesn't seem to be running."
    echo "Would you like to start it? (y/n)"
    read -r start_proxy

    if [[ $start_proxy == "y" || $start_proxy == "Y" ]]; then
        echo "Starting A-Proxy..."
        if [ -d "../venv" ]; then
            cd .. && source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
            python app.py --port 5002 &
            cd - > /dev/null
            PROXY_PID=$!
            echo "A-Proxy starting with PID: $PROXY_PID"
            echo "Waiting for A-Proxy to start..."
            sleep 5
        else
            echo "Could not find venv. Please start A-Proxy manually."
            exit 1
        fi
    else
        echo "Please start A-Proxy manually and run this script again."
        exit 1
    fi
fi

# Create directories
mkdir -p screenshots videos

# Run the demo
echo "Starting A-Proxy feature demonstration..."
python demo_script.py

if [ $? -eq 0 ]; then
    echo ""
    echo "Demo completed successfully!"
    echo "Screenshots saved to: ./screenshots"
    echo "Video saved to: ./videos"
    echo ""
    echo "Would you like to generate a PDF report? (y/n)"
    read -r gen_pdf

    if [[ $gen_pdf == "y" || $gen_pdf == "Y" ]]; then
        echo "Generating PDF report..."
        python create_pdf_report.py

        if [ $? -eq 0 ]; then
            echo "PDF report generated: A-Proxy-Demo-Report.pdf"
        else
            echo "Error generating PDF report."
        fi
    fi
else
    echo "Demo did not complete successfully. Check the console output for errors."
fi
