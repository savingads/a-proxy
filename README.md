# A-Proxy

A Flask-based web application for persona-driven AI interactions and conversation archiving. Chat as different personas with configurable demographic, psychographic, and behavioral attributes that influence AI model responses.

## Features

- **Persona Management**: Create and manage detailed personas with demographic, behavioral, and contextual attributes
- **AI Chat Integration**: Chat with Claude AI models from different persona perspectives
- **Conversation Archiving**: Automatically archive conversations with metadata for analysis
- **Journey Tracking**: Track persona interaction sessions over time
- **Geolocation Support**: IP-based and browser geolocation for contextual interactions
- **Docker Ready**: Fully containerized for easy deployment

## Quick Start with Docker (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- (Optional) Anthropic API key for AI chat features

### 1. Clone and Build
```bash
git clone <repository-url>
cd a-proxy
docker compose build
```

### 2. Start the Application
```bash
# Start without AI features (for testing/demo)
docker compose up -d

# OR start with AI features
ANTHROPIC_API_KEY=your-api-key-here docker compose up -d
```

### 3. Access the Application
- Open http://localhost:5002
- Login with: `admin@example.com` / `password`

## Manual Setup (Development)

### Prerequisites
- Python 3.8+ with pip
- Node.js with npm (for frontend assets)
- Git

### 1. Clone and Setup Environment
```bash
git clone <repository-url>
cd a-proxy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install
```

### 2. Configure Environment
```bash
# Copy and edit environment file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Initialize Database
```bash
mkdir -p data
python database.py
python create_sample_personas_simple.py  # Optional: create sample data
python init_default_user.py  # Create default admin user
```

### 4. Run the Application
```bash
python app.py
```

The application will be available at http://localhost:5002

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key for AI features | (empty) |
| `SECRET_KEY` | Flask session secret | `dev-secret-key-change-in-production` |
| `DEBUG` | Enable debug mode | `False` |

### Default Credentials

For testing and demo purposes, a default admin user is automatically created:
- **Email**: `admin@example.com`
- **Password**: `password`

**Change these credentials in production environments**

## Core Features

### Persona Management
- Create personas with detailed attributes:
  - **Demographic**: Age, gender, location, education, income
  - **Psychographic**: Interests, values, attitudes, lifestyle
  - **Behavioral**: Browsing habits, device usage, social media activity
  - **Contextual**: Time of day, weather, device type, connection

### AI Chat Integration
- Chat with Claude AI models as different personas
- Persona attributes influence AI responses
- Conversation history and context management
- Model parameter tracking for analysis

### Journey Tracking
- Create browsing/interaction sessions
- Track waypoints and conversation progression
- Archive sessions with full metadata

### Data Architecture
- SQLite database for persistence
- Integrated persona management (no separate microservice)
- Comprehensive data relationships and indexing

## API Endpoints

### Core Routes
- `/` - Home dashboard
- `/login` - User authentication
- `/personas` - Persona management
- `/interact-as` - Choose persona for interaction
- `/direct-chat/<persona_id>` - AI chat interface
- `/journeys` - Journey tracking
- `/archives` - Conversation archives

## Security Features

### Docker Security
- API keys excluded from Docker images
- Runtime environment variable injection
- Secure defaults for production deployment

See [DOCKER_SECURITY.md](DOCKER_SECURITY.md) for detailed security information.

### Best Practices
- Secrets managed via environment variables
- Session security with secure cookies
- Input validation and sanitization
- Database query parameterization

## Development

### Project Structure
```
a-proxy/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── database.py           # Database initialization
├── routes/               # Blueprint route handlers
├── templates/            # Jinja2 HTML templates
├── static/              # CSS, JS, and static assets
├── utils/               # Utility modules
├── data/                # SQLite database storage
└── docker-compose.yml   # Docker configuration
```

### Adding New Features
1. Create new routes in `routes/` directory
2. Add corresponding templates in `templates/`
3. Update database schema in `database.py` if needed
4. Add static assets to `static/` directory

### Testing
```bash
# Run basic functionality tests
curl http://localhost:5002/
curl http://localhost:5002/personas
curl http://localhost:5002/dashboard
```

## Troubleshooting

### Common Issues

**Port 5002 in use**
```bash
# Use different port
python app.py --port 5003
```

**Database issues**
```bash
# Reinitialize database
rm data/personas.db
python database.py
python create_sample_personas_simple.py
```

**Missing dependencies**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### WSL Users
```bash
# Keep project files within WSL filesystem for better performance
# Install build dependencies
sudo apt-get install build-essential python3-dev

# For Pillow issues
sudo apt-get install libjpeg-dev libpng-dev libtiff-dev
```

### Docker Issues
```bash
# Rebuild container completely
docker compose down
docker compose build --no-cache
docker compose up -d

# Check container logs
docker logs a-proxy-a-proxy-1
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Development Credits
STATEMENT ON THE USE OF GENERATIVE AI:
This project was developed with significant assistance from generative AI (Claude), which handled the majority of the coding, debugging, and documentation work while the human developers primarily ate snacks and occasionally pressed "1" to approve suggestions. 

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3). This means:

- You can freely use, modify, and distribute this software
- Any derivative works must also be licensed under GPL-3
- Commercial use requires proper attribution and compliance with GPL-3 terms
- Source code must be made available when distributing the software

See the full GPL-3 license text at: https://www.gnu.org/licenses/gpl-3.0.en.html

## Support

For issues and questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review existing issues in the repository
3. Create a new issue with detailed information

---

**Note**: This application is designed for research and testing purposes. Ensure compliance with AI service terms of use and data privacy regulations in your jurisdiction.