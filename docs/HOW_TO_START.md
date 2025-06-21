# A-Proxy: How to Start the Application

There are two main ways to run A-Proxy: using Docker (recommended) or manual installation.

## Option 1: Using Docker (Recommended)

Docker provides the easiest setup experience by handling all dependencies and environment configuration automatically.

### Quick Start with Docker

1. Run the provided helper script:
   ```bash
   ./start-a-proxy.sh
   ```

2. Access the application in your browser:
   ```
   http://localhost:5002
   ```

For detailed Docker instructions, advanced configuration options, and troubleshooting, see [DOCKER.md](DOCKER.md).

## Option 2: Manual Installation (Updated)

### Prerequisites

1. Python 3.8+ with pip
2. Node.js with npm
3. Git for version control

### Quick Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY for Claude integration
   ```

3. **Initialize the database**:
   ```bash
   mkdir -p data
   python database.py
   python create_sample_personas_simple.py  # Optional: Add sample data
   ```

4. **Start the application**:
   ```bash
   python app.py
   ```

The application will be available at http://localhost:5002

### Default Login Credentials

When you first start the application, use these credentials to log in:
- **Email**: admin@example.com
- **Password**: password

**Important**: Change these credentials in production environments!

### Custom Port Configuration

If port 5002 is already in use, you can specify a different port:

```bash
python app.py --port 5003
```

## Troubleshooting

### Docker Issues

See [DOCKER.md](DOCKER.md) for Docker-specific troubleshooting.

### Manual Installation Issues

**Common Issues:**
- **Port conflicts**: Use `--port` option to specify different port
- **Database issues**: Remove `data/personas.db` and run `python database.py` to reinitialize
- **Missing dependencies**: Ensure virtual environment is activated and run `pip install -r requirements.txt`

**For detailed setup instructions and troubleshooting, see the main [CLAUDE.md](../CLAUDE.md) file.**
