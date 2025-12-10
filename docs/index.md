# A-Proxy Documentation

A-Proxy is a persona-driven web archiving system that enables targeted web crawling from specific user perspectives while preserving LLM interactions for research.

## Core Goals

A-Proxy serves two primary archival objectives:

1. **Persona-Driven Web Crawling**: Create detailed persona representations to enable targeted web crawling from specific demographic, behavioral, and contextual perspectives.

2. **LLM Evolution Documentation**: Archive chat interactions to study how large language models respond to different persona contexts over time.

## How It Works

### Workflow

1. **Persona Creation**: Archivists create personas with four attribute categories (demographic, psychographic, behavioral, contextual) through the web interface.

2. **Chat-Assisted Development**: Optional conversations with Claude AI help explore persona characteristics. Archivists then manually update persona profiles based on insights from the conversation.

3. **Targeted Browsing**: Browse websites with browser variables configured to reflect persona characteristics (location via VPN, language, user-agent).

4. **Archiving**: Capture web pages as they appear to the configured persona, preserving both content and context.

5. **Research Value**: Preserved archives document personalized web experiences; chat logs document LLM interactions with different persona contexts.

## Key Features

| Feature | Description |
|---------|-------------|
| Persona Management | Create and manage user personas with 4-dimensional attributes |
| Journey Tracking | Record sequences of web interactions as "journeys" with "waypoints" |
| Web Archiving | Archive webpages with persona-specific context (language, geolocation) |
| Claude AI Chat | Chat with Claude AI as or about a persona |
| VPN Integration | Browse from different geographic regions using NordVPN |

## Current Capabilities

**Working:**

- Full CRUD for personas with all 4 dimensions
- Journey and waypoint management
- Claude AI chat (requires API key)
- VPN integration (requires NordVPN setup)
- Web page archiving with screenshots
- Internet Archive submission

**Manual processes:**

- Persona attribute updates after chat sessions
- Archive comparison (no built-in diff tool)

## Use Cases

- Targeted web archiving from diverse demographic perspectives
- Documenting how different user groups experience websites
- Preserving persona-LLM interactions for future research
- Creating archival records that reflect multiple viewpoints

## Getting Started

<div class="grid cards" markdown>

-   **Installation**

    ---

    Set up A-Proxy on your local machine or server

    [:octicons-arrow-right-24: Installation Guide](getting-started/installation.md)

-   **First Login**

    ---

    Log in and explore the interface

    [:octicons-arrow-right-24: First Login](getting-started/first-login.md)

</div>

## Quick Links

- [Persona Model](concepts/persona-model.md) - Understanding the 4-dimensional persona framework
- [Journeys and Waypoints](concepts/journeys-waypoints.md) - Tracking user interactions
- [Create Personas](how-to/create-personas.md) - Step-by-step persona creation
- [API Reference](reference/api-endpoints.md) - Complete API documentation
