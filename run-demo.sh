#!/bin/bash

# Redirect script for A-Proxy Demonstration

echo "========================================================="
echo "The A-Proxy demo scripts have been moved to the demo directory."
echo "========================================================="
echo ""
echo "To run the demonstration, please use:"
echo ""
echo "    cd demo"
echo "    ./run-demo.sh"
echo ""
echo "Or to run it now, type 'y':"

read -r run_now

if [[ $run_now == "y" || $run_now == "Y" ]]; then
    echo "Running demo script from demo directory..."
    cd demo && ./run-demo.sh
else
    echo "Exiting. You can run the demo later using the commands above."
fi
