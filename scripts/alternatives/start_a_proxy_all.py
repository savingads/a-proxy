#!/usr/bin/env python3
"""
Startup script for A-Proxy with all implementation options
"""
import argparse
import subprocess
import os
import sys
import time
import signal
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('startup')

# Process handle for the API server (when started)
api_server_process = None

def signal_handler(sig, frame):
    """Handle termination signals"""
    logger.info("Shutting down...")
    if api_server_process:
        logger.info("Terminating API service...")
        api_server_process.terminate()
        api_server_process.wait()
    sys.exit(0)

def start_api_service():
    """Start the Persona API service"""
    api_dir = Path('persona-service')
    if not api_dir.exists():
        logger.error(f"API service directory not found: {api_dir}")
        return None
    
    try:
        logger.info("Starting Persona API service...")
        process = subprocess.Popen(
            [sys.executable, 'run.py'],
            cwd=api_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Wait for the API service to start (output the first few lines)
        for _ in range(10):
            line = process.stdout.readline()
            if not line:
                break
            logger.info(f"[API] {line.strip()}")
            if "Running on" in line:
                logger.info("API service is running")
                break
        
        # Start a thread to continuously read and log output
        def log_output(process):
            for line in process.stdout:
                logger.info(f"[API] {line.strip()}")
        
        import threading
        threading.Thread(target=log_output, args=(process,), daemon=True).start()
        
        # Give the server a moment to initialize
        time.sleep(2)
        
        return process
    except Exception as e:
        logger.error(f"Failed to start API service: {str(e)}")
        return None

def start_main_app(implementation='api', use_fixed=True):
    """
    Start the main application
    
    Args:
        implementation: The implementation to use ('api', 'mock', or 'db')
        use_fixed: Whether to use the fixed implementation
    """
    if implementation == 'api':
        app_file = 'app_fixed.py' if use_fixed else 'app.py'
    elif implementation == 'mock':
        app_file = 'app_with_mock_fixed.py' if use_fixed else 'app_with_mock.py'
    elif implementation == 'db':
        app_file = 'app_with_db.py'
    else:
        logger.error(f"Unknown implementation: {implementation}")
        return None
    
    try:
        logger.info(f"Starting A-Proxy using {app_file}...")
        process = subprocess.run(
            [sys.executable, app_file],
            check=True
        )
        return process
    except subprocess.CalledProcessError as e:
        logger.error(f"Application exited with error code {e.returncode}")
        return None
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Start A-Proxy with different configuration options')
    parser.add_argument('--implementation', choices=['api', 'mock', 'db'], default='db',
                      help='Implementation to use: api (external API), mock (in-memory data), or db (SQLite database)')
    parser.add_argument('--api-only', action='store_true', help='Start only the API service')
    parser.add_argument('--app-only', action='store_true', help='Start only the main application')
    parser.add_argument('--original', action='store_true', help='Use original implementation (not fixed versions)')
    
    args = parser.parse_args()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    global api_server_process
    
    try:
        # Start API service if using API implementation (unless app-only)
        if args.implementation == 'api' and not args.app_only:
            api_server_process = start_api_service()
            if not api_server_process and not args.api_only:
                logger.warning("Failed to start API service. Consider using --implementation=mock or --implementation=db")
                choice = input("Would you like to continue with a different implementation? (mock/db/n): ").lower()
                if choice == 'mock':
                    args.implementation = 'mock'
                elif choice == 'db':
                    args.implementation = 'db'
                else:
                    return 1
        
        # Start main application (unless api-only)
        if not args.api_only:
            app_process = start_main_app(
                implementation=args.implementation, 
                use_fixed=not args.original
            )
            if not app_process:
                logger.error("Failed to start main application")
                return 1
        else:
            # If only starting API, keep the script running
            logger.info("API service running. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    finally:
        if api_server_process:
            logger.info("Terminating API service...")
            api_server_process.terminate()
            api_server_process.wait()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
