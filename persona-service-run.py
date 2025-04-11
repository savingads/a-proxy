#!/usr/bin/env python3
"""
Entry point for running the Persona Service
"""
import argparse
from app import create_app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Persona Service API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=5050, help="Port to run the server on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")

    args = parser.parse_args()

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)
