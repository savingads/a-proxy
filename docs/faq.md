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

- Python 3.10 or higher (3.12+ recommended)
- Playwright Chromium browser (installed via `python -m playwright install chromium`)
- An LLM endpoint: local (vLLM, Ollama) or cloud API key (Anthropic, OpenAI)

### Do I need Docker?

No. A-Proxy runs natively on Windows, macOS, and Linux. Docker is available as a deployment option but is not required.

### Can I run A-Proxy without an LLM?

The core features (persona management, browsing, archiving) work without an LLM. Chat features require at least one LLM provider configured.

## Personas

### What are the four persona dimensions?

1. **Demographic**: Observable characteristics (location, age, occupation)
2. **Psychographic**: Internal attributes (interests, values, personality)
3. **Behavioral**: Online actions (browsing habits, device usage)
4. **Contextual**: Situational factors (time of day, device type)

See [Persona Model](concepts/persona-model.md) for details.

### How do personas affect web browsing?

Persona attributes configure browser settings via Playwright:

- Geographic location via proxy + geolocation emulation
- Language via locale setting
- Timezone via timezone emulation
- Screen size via viewport settings

### Can personas be developed through conversation?

Yes. Chat with an LLM as or about a persona to develop attributes organically. The system can extract information from conversations to update persona profiles.

## Journeys and Waypoints

### What is a journey?

A journey is a named collection of interactions performed as a specific persona. It organizes browsing sessions and chat conversations into a coherent sequence.

### What is a waypoint?

A waypoint is a single interaction within a journey. Types include:

- **Browse waypoints**: Web page visits
- **Agent waypoints**: Chat conversations with an LLM

### How are waypoints ordered?

Waypoints have sequence numbers assigned automatically based on creation order within a journey.

## Proxy & Geo-IP

### Do I need a VPN?

No. A-Proxy uses SOCKS5/HTTP proxies instead of VPN software. Proxies are configured per browser context through Playwright, so no system-wide VPN is needed.

### What proxy services work?

Any SOCKS5 or HTTP proxy works. Options include residential proxy services, datacenter proxies, SSH tunnels, or self-hosted proxies.

### Can I use A-Proxy without a proxy?

Yes. Proxy is optional. Without a proxy, browsing uses your actual network location. Playwright still emulates geolocation coordinates, locale, and timezone regardless.

## Web Archiving

### What is captured when archiving a page?

- HTML source
- Screenshot of rendered page
- Metadata (persona context, timestamps)

### Where are archives stored?

In the `archives/` directory, organized by URL hash and timestamp.

### Does A-Proxy interact with the Internet Archive?

Integration with the Internet Archive is configurable but separate from local archiving.

## LLM Integration

### Which LLM providers are supported?

- **Local/self-hosted**: Any OpenAI-compatible endpoint (vLLM, Ollama, text-generation-webui, LiteLLM)
- **Anthropic**: Claude
- **OpenAI**: GPT

### How do I use a local model?

Install [Ollama](https://ollama.com) and set:
```bash
OPENAI_COMPATIBLE_URL=http://localhost:11434/v1
OPENAI_COMPATIBLE_MODEL=qwen2.5:7b
```

For HPC deployments (e.g., vLLM on a GPU cluster), point to the vLLM endpoint.

### Are conversations stored?

Yes. Agent waypoints store conversation history as JSON for research purposes.

## Technical Issues

### Database errors on startup

Try removing and reinitializing:

```bash
rm -f data/personas.db
python init_default_user.py
```

### Port 5002 already in use

Specify a different port:

```bash
python app.py --port 5003
```

### Pages not loading during browsing

Check:

1. Internet connectivity
2. Proxy connection status (if enabled)
3. Target site accessibility

### Playwright browser not found

Install the Chromium browser:

```bash
python -m playwright install chromium
```

### Missing persona data after update

Ensure all dimension tables exist. The database auto-initializes on import of the `database` package.

## Data and Privacy

### Where is data stored?

All data is stored locally:

- Database: `data/personas.db`
- Archives: `archives/`

### Is data encrypted?

No encryption at rest is implemented. This is intended for local/research use.

### Can data be exported?

Journey and persona data can be exported as JSON through the interface.

## Development

### How do I run tests?

```bash
python -m pytest tests/
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

Report issues at the [project repository](https://github.com/savingads/a-proxy/issues).
