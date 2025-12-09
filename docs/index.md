# A-Proxy Documentation

A-Proxy is a persona-driven web archiving system that enables targeted web crawling from specific user perspectives while preserving LLM interactions for research.

## Core Goals

A-Proxy serves two primary archival objectives:

1. **Persona-Driven Web Crawling**: Develop detailed persona representations through cumulative chat conversations to enable targeted web crawling from specific perspectives.

2. **LLM Evolution Documentation**: Archive chat interactions to study how large language models develop over time and respond to increasing personalization.

## How It Works

The system operates through a feedback loop:

```
Persona Generation --> Persona Development via Chat --> Targeted Crawling --> Dual Archival Value
```

### The Feedback Loop

1. **Persona Generation**: Archivists create initial personas across four data categories (demographic, psychographic, behavioral, contextual) with LLM assistance.

2. **Persona Development**: Through chat conversations, personas evolve and gain depth. Relevant features are reified to build components that browsers and content delivery systems use for targeting.

3. **Targeted Crawling**: Archivists crawl websites from persona perspectives. Browser variables reflect persona characteristics (location, language, user-agent), cookies set context, and browsing sessions capture how different users experience the web.

4. **Dual Archival Value**: Refined personas enable crawls from specific perspectives while preserved chats document LLM behavior changes over time.

## Key Features

| Feature | Description |
|---------|-------------|
| Persona Management | Create and manage user personas with 4-dimensional attributes |
| Journey Tracking | Record sequences of web interactions as "journeys" with "waypoints" |
| Web Archiving | Archive webpages with persona-specific context (language, geolocation) |
| AI Integration | Chat with Claude AI as or about a persona to develop attributes |
| VPN Simulation | Test from different geographic regions using VPN integration |

## Use Cases

- Targeted web archiving from diverse demographic perspectives
- Documenting how different user groups experience websites
- Preserving persona-LLM interactions for future research
- Studying LLM behavioral changes over time
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
