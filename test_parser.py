import argparse

def test_parser():
    parser = argparse.ArgumentParser(description='Run the Flask application')
    parser.add_argument('--port', type=int, default=5002, help='Port to run the application on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host address to run the application on')
    
    # Parse the args and print them to verify
    args = parser.parse_args()
    print(f"Arguments parsed successfully:")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")

if __name__ == "__main__":
    test_parser()
