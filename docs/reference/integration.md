# Integration

A-Proxy is designed to integrate with OntServe (ontology management) and ProEthica (professional ethics analysis). This document describes the integration architecture and current implementation status.

## Integration Goals

1. **Import role definitions** from OntServe ontologies
2. **Attach ethical frameworks** from ProEthica
3. **Instantiate personas** with ontology-backed attributes
4. **Export personas** as semantic web artifacts (RDF/OWL)

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   OntServe                       │
│   Ontology Storage, Querying, Reasoning         │
│   REST API / SPARQL                             │
└────────────────────────┬────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         v               v               v
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   A-Proxy   │  │  ProEthica  │  │ Other MCP   │
│             │  │             │  │  Clients    │
│ - Persona   │  │ - Ethical   │  │             │
│   Mgmt      │  │   Analysis  │  │             │
│ - Journey   │  │ - Case      │  │             │
│   Tracking  │  │   Review    │  │             │
│ - MCP       │  │ - MCP       │  │             │
│   Client    │  │   Client    │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
```

## Data Flow

1. **Role Import**: A-Proxy queries OntServe for role class definitions
2. **Ethical Binding**: ProEthica provides ethical constraints for professional roles
3. **Persona Creation**: User creates persona from role template plus custom attributes
4. **Simulation**: Claude AI responses informed by role and ethical context
5. **Export**: Persona data exported as RDF for ontology integration

## Current vs. Target State

| Aspect | Current | Target |
|--------|---------|--------|
| Schema | Fixed 4-dimension model | Extensible ontology-driven |
| Roles | Implicit (occupation field) | Explicit role classes from OntServe |
| Ethics | None | ProEthica ethical framework |
| Export | JSON | RDF/Turtle/JSON-LD |
| Interoperability | Standalone | MCP-connected ecosystem |

## Implementation Status

### Phase 1: Standalone Refactoring (Complete)

- Repository pattern for database access
- Domain models as dataclasses
- Test suite passing

### Phase 2: Service Layer (Planned)

- Service layer abstraction
- Basic ontology export capability
- RDF serialization

### Phase 3: OntServe Integration (Planned)

- MCP client for OntServe queries
- Role import from ontologies
- Persona-to-ontology mapping

### Phase 4: ProEthica Integration (Planned)

- Ethical framework attachment
- Role-based ethical constraints
- Decision scenario integration

## MCP Protocol

Model Context Protocol (MCP) enables service communication:

```json
{
    "jsonrpc": "2.0",
    "method": "query_role",
    "params": {
        "role_uri": "aproxy:MechanicalEngineer"
    },
    "id": 1
}
```

## Ontology Namespace

```turtle
@prefix aproxy: <http://ontorealm.net/aproxy#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix schema: <http://schema.org/> .

aproxy:Persona a owl:Class ;
    rdfs:subClassOf foaf:Person .

aproxy:hasRole a owl:ObjectProperty ;
    rdfs:domain aproxy:Persona ;
    rdfs:range aproxy:Role .
```

## Related Systems

### OntServe

Ontology management system providing:

- PostgreSQL-backed ontology storage
- SPARQL query interface
- Reasoning capabilities
- MCP server for inter-service communication

URL: `https://ontserve.ontorealm.net`

### ProEthica

Professional ethics analysis system providing:

- 9-concept extraction framework
- Case analysis methodology
- Ethical precedent discovery
- MCP server for ethics queries

URL: `https://proethica.org`

## Configuration

Integration settings in `.env`:

```bash
ONTSERVE_URL=http://localhost:8082
PROETHICA_URL=http://localhost:5000
MCP_ENABLED=false
```

## Related Documentation

- [System Architecture](architecture.md) - A-Proxy architecture
- [Database Schema](database-schema.md) - Data storage
- [Persona Model](../concepts/persona-model.md) - 4-dimensional model
