# Archival Goals

A-Proxy serves two complementary archival objectives that together provide unique research value for understanding both web content personalization and LLM behavior.

## Dual Archival Purpose

### 1. Persona-Driven Web Crawling

Traditional web archiving captures a single, generic view of web content. However, modern websites deliver personalized experiences based on user attributes such as:

- Geographic location
- Language preferences
- Browsing history
- Device characteristics
- Time of access

A-Proxy enables **targeted web crawling from specific perspectives** by:

- Developing detailed persona representations through cumulative interactions
- Configuring browser variables to reflect persona characteristics
- Capturing how different user types experience the same content
- Preserving the personalized web as it was presented to specific audiences

### 2. LLM Evolution Documentation

As large language models evolve, their responses to personalization change. A-Proxy archives chat interactions to:

- Document how LLMs respond to increasing personalization
- Track changes in model behavior across versions
- Benchmark responses based on persona characteristics
- Preserve conversational context for future research

## The Personalization Challenge

Modern web pages present different content based on user attributes:

| Attribute | Web Impact |
|-----------|------------|
| Location (GeoIP) | Local news, weather, regional pricing |
| Language | Interface language, content translation |
| Browsing History | Recommendations, targeted advertising |
| Device Type | Layout, feature availability |
| Time of Day | Content freshness, regional updates |

Traditional archiving methods capture only one version, losing the rich diversity of personalized experiences.

## Research Applications

### Web Archive Research

- **Demographic Perspectives**: How did different user groups experience a website during a historical event?
- **Regional Variations**: What content differences existed between geographic regions?
- **Temporal Analysis**: How did personalization strategies evolve over time?

### LLM Research

- **Personalization Response**: How do LLMs adapt their communication style to different personas?
- **Consistency Analysis**: Are LLM responses consistent across similar persona types?
- **Evolution Tracking**: How have LLM personalization capabilities changed between versions?

## Retrieval and Replay

A-Proxy addresses the two key phases of personalized archiving:

### Retrieval Phase

Capturing web content comprehensively:

- Static elements (HTML, CSS)
- Dynamic content (JavaScript-rendered elements)
- Personalization layers (recommendations, location-based content)
- Contextual metadata (user-agent, cookies, geolocation)

### Replay Phase

Recreating captured content faithfully:

- Session reconstruction with original user context
- Browser environment simulation
- Dynamic feature preservation
- Temporal comparison support

## Ontology-Based Organization

A-Proxy uses ontology concepts to organize user attributes:

| Data Category | Ontology Entity | Purpose |
|---------------|-----------------|---------|
| Demographic | CCO:Agent | User profile classification |
| Behavioral | BFO:Occurrent | Activity pattern tracking |
| Psychographic | BFO:SpecificallyDependentContinuant | Preference modeling |
| Contextual | BFO:SpatialRegion, BFO:TemporalRegion | Environment simulation |

This structured approach enables:

- Systematic persona comparison
- Cross-archive analysis
- Research reproducibility

## Related Concepts

- [Persona Model](persona-model.md) - The 4-dimensional attribute framework
- [Journeys and Waypoints](journeys-waypoints.md) - Tracking interaction sequences
