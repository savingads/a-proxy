# A-Proxy Project State Documentation

## Project Overview

A-Proxy is a Flask-based web application that allows users to browse the web through different personas with geolocation and language emulation. The application integrates VPN connections, user profiles (personas), and AI assistance through Claude integration.

## Current State of the Project

### Core Functionality
1. **Persona Management**: Dynamic system for creating and managing user personas with demographic, psychographic, behavioral, and contextual attributes
2. **Journey Tracking**: Users can create journeys (browsing sessions) with waypoints to track their web exploration
3. **Archive System**: Captures and stores web content with metadata and screenshots
4. **AI Integration**: Claude API integration for chat functionality and journey assistance
5. **Authentication**: User login system with Flask-Login

### Architecture
- **Main Application**: Flask app (`app.py`) running on port 5002
- **Integrated Persona Management**: Direct database access via `routes/persona_api_db.py`
- **Database**: SQLite database (`data/personas.db`) for persistent storage
- **Frontend**: Bootstrap-based UI with JavaScript for interactive features

### Key Components

#### Routes/Blueprints
- `home`: Dashboard and main navigation
- `auth`: User authentication (login/register)
- `persona_api`: Persona management through API
- `browsing`: Web browsing functionality
- `archives`: Web content archiving
- `journey`: Journey creation and management
- `agent`: AI chat integration
- `vpn`: VPN management (legacy/optional)

#### Services
- **Persona Service**: Standalone API service for persona management
- **Agent Module**: Claude integration for AI assistance
- **Internet Archive**: Integration for archiving web content

### Configuration Issues

**Missing `config.py` file**: The application expects a `config.py` module that doesn't exist. This file should contain:
- `SECRET_KEY`: Flask secret key for sessions
- `SESSION_COOKIE_SECURE`: Boolean for secure cookies
- `SESSION_COOKIE_HTTPONLY`: Boolean for HTTP-only cookies
- `SESSION_COOKIE_SAMESITE`: Cookie same-site policy

### Dependencies
- Flask and related packages (Flask-WTF, Flask-Login, Flask-CORS)
- SQLAlchemy for database ORM
- Selenium for web browsing automation
- Anthropic SDK for Claude integration
- Various utility libraries (cryptography, requests, python-dotenv)

### Startup Process
The recommended way to start the application is using `start.sh`, which:
1. Checks repository status
2. Activates virtual environment
3. Ensures required dependencies are installed
4. Initializes databases
5. Starts A-Proxy application (port 5002)

### Current Issues to Address

1. **Missing `config.py`**: Need to create this file with proper Flask configuration
2. **Environment Variables**: Need to set up `.env` file based on `.env.example`
3. **Dependency Installation**: Ensure all requirements are properly installed
4. **Database Initialization**: Verify database tables are created
5. **Source Repositories**: The `_src/` directory structure needs to be set up properly

### Recent Updates (from existing CLAUDE.md)
- Production deployment workflow implemented with Digital Ocean support
- Dashboard page created with system status visualization
- Chat feature enhanced with journey integration
- Conversation continuity implemented for waypoints
- Context management system added for Claude interactions
- UI refinements for better user experience

## Setup Instructions

### Prerequisites
- Python 3.8+ with pip
- Node.js with npm (for frontend assets)
- Git for version control

### Quick Setup

1. **Clone and enter the repository**:
   ```bash
   git clone <repository-url>
   cd a-proxy
   ```

2. **Create and activate Python virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY for Claude integration
   ```

5. **Initialize the database**:
   ```bash
   mkdir -p data
   python database.py
   python create_sample_personas_simple.py  # Optional: create sample data
   ```

6. **Run the application**:
   ```bash
   python app.py
   ```

The application will be available at http://localhost:5002

### Development Notes

- The persona service has been integrated directly into the main application (no separate microservice needed)
- All persona data is stored in SQLite database (`data/personas.db`)
- The app supports dynamic persona creation with demographic, psychographic, behavioral, and contextual data
- Docker deployment is available via `./start-a-proxy.sh` script

### Recent Updates

**2025-06-20: Persona Service Integration**
- Integrated persona service directly into main application
- Replaced API-based persona management with direct database access
- Created comprehensive persona database schema with proper data relationships
- Added sample persona creation functionality
- Eliminated dependency on separate persona-service microservice

**2025-04-18: Production Deployment & UI Improvements**
- Implemented production deployment workflow with Digital Ocean support
- Enhanced chat and journey integration with conversation continuity
- Added context management system for Claude interactions
- Improved dashboard with system status visualization
- Streamlined UI and navigation flow

### Troubleshooting

**Common Issues:**
- **Port 5002 in use**: Use `python app.py --port 5003` to specify different port
- **Database issues**: Remove `data/personas.db` and run `python database.py` to reinitialize
- **Missing dependencies**: Ensure virtual environment is activated and run `pip install -r requirements.txt`

**WSL Users:**
- Keep project files within WSL file system for better performance
- Install build dependencies: `sudo apt-get install build-essential python3-dev`
- For Pillow issues: `sudo apt-get install libjpeg-dev libpng-dev libtiff-dev`

The project is a sophisticated web browsing proxy with persona simulation, journey tracking, and AI assistance capabilities. The modular architecture allows for flexible deployment and development.