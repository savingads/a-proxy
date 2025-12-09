# Frequently Asked Questions

## General Questions

### What is A-Proxy?

A-Proxy is a persona simulation and web interaction tracking system designed for archival research. It enables researchers to create detailed user personas and capture web content from those personas' perspectives.

### What are the primary use cases?

1. **Persona-driven web archiving**: Capturing web content as it appears to users with specific demographic, psychographic, behavioral, and contextual attributes
2. **LLM interaction research**: Documenting how large language models respond to different persona contexts over time

### What is the relationship with OntServe and ProEthica?

A-Proxy is part of a larger ontology-driven research ecosystem:

- **OntServe**: Provides ontology storage and querying for role definitions
- **ProEthica**: Provides professional ethics frameworks

Integration with these systems is planned but not yet implemented.

## Installation

### What are the system requirements?

- Python 3.8 or higher
- Node.js (for frontend dependencies)
- Docker (recommended for full functionality)
- Chromium browser (for web archiving)

### Why is Docker recommended?

Docker provides:

- Consistent environment across systems
- Simplified VPN integration
- Isolated browser instances
- Easier dependency management

### Can I run A-Proxy without Docker?

Yes. Manual installation is supported. See [Installation](getting-started/installation.md) for both methods.

## Personas

### What are the four persona dimensions?

1. **Demographic**: Observable characteristics (location, age, occupation)
2. **Psychographic**: Internal attributes (interests, values, personality)
3. **Behavioral**: Online actions (browsing habits, device usage)
4. **Contextual**: Situational factors (time of day, device type)

See [Persona Model](concepts/persona-model.md) for details.

### How do personas affect web browsing?

Persona attributes configure browser settings:

- Geographic location via VPN
- Language via Accept-Language header
- Device via User-Agent string
- Screen size via viewport settings

### Can personas be developed through conversation?

Yes. Chat with Claude AI as or about a persona to develop attributes organically. The system can extract information from conversations to update persona profiles.

## Journeys and Waypoints

### What is a journey?

A journey is a named collection of interactions performed as a specific persona. It organizes browsing sessions and chat conversations into a coherent sequence.

### What is a waypoint?

A waypoint is a single interaction within a journey. Types include:

- **Browse waypoints**: Web page visits
- **Agent waypoints**: Chat conversations with Claude

### How are waypoints ordered?

Waypoints have sequence numbers assigned automatically based on creation order within a journey.

## VPN Integration

### Which VPN services are supported?

Currently, NordVPN is supported via OpenVPN configuration files.

### Why might VPN not work?

Common causes:

- Invalid credentials in `nordvpn/auth.txt`
- Missing OpenVPN configuration files
- Target site blocking VPN traffic
- Firewall restrictions

### Can I use A-Proxy without VPN?

Yes. VPN is optional. Without VPN, browsing uses your actual network location.

## Web Archiving

### What is captured when archiving a page?

- HTML source
- Screenshot of rendered page
- HTTP headers
- Metadata (persona context, timestamps)

### Where are archives stored?

In the `archives/` directory, organized by date.

### Does A-Proxy interact with the Internet Archive?

Integration with the Internet Archive is configurable but separate from local archiving.

## Claude AI Integration

### How is Claude used in A-Proxy?

Claude AI enables:

- Conversational persona development
- Browsing-related queries as a persona
- Research assistance from persona perspective

### What API key is required?

An Anthropic API key (`ANTHROPIC_API_KEY`) is required for Claude integration.

### Are conversations stored?

Yes. Agent waypoints store conversation history as JSON for research purposes.

## Technical Issues

### Database errors on startup

Try removing and reinitializing:

```bash
rm data/personas.db
python -c "from database import initialize_database; initialize_database()"
```

### Port 5002 already in use

Specify a different port:

```bash
python app.py --port 5003
```

### Pages not loading during browsing

Check:

1. Internet connectivity
2. VPN connection status (if enabled)
3. Target site accessibility

### Missing persona data after update

Ensure all dimension tables exist. Run database initialization:

```python
from database import create_persona_tables
create_persona_tables()
```

## Data and Privacy

### Where is data stored?

All data is stored locally:

- Database: `data/personas.db`
- Archives: `archives/`
- VPN credentials: `nordvpn/auth.txt`

### Is data encrypted?

No encryption at rest is implemented. This is intended for local/research use.

### Can data be exported?

Journey and persona data can be exported as JSON through the interface.

## Development

### How do I run tests?

```bash
python tests/test_runner.py
```

### What is the repository pattern?

Data access uses repository classes that encapsulate database operations:

```python
from database.repositories import PersonaRepository
repo = PersonaRepository()
persona = repo.get(1)
```

### How do I add new endpoints?

1. Create a blueprint in `routes/`
2. Register in `app.py`
3. Add templates in `templates/`

## Getting Help

### Where can I report issues?

Report issues at the project repository.

### Is there a community forum?

Not currently. For questions, open an issue on the repository.
