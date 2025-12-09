# A-Proxy Integration Plan

This document outlines the integration strategy for connecting A-Proxy with OntServe (ontology server) and Proethica (ethical decision-making framework) to create a unified persona modeling ecosystem.

## Table of Contents

1. [Vision](#vision)
2. [Integration Architecture](#integration-architecture)
3. [Phase Implementation Plan](#phase-implementation-plan)
4. [Ontology Design](#ontology-design)
5. [MCP Integration](#mcp-integration)
6. [Use Cases](#use-cases)
7. [Technical Specifications](#technical-specifications)

---

## Vision

The goal is to transform A-Proxy from a standalone persona simulation tool into an ontology-driven persona instantiation system that can:

1. **Import role definitions** from OntServe (e.g., "Mechanical Engineer", "High School Teacher")
2. **Attach ethical frameworks** from Proethica (professional codes, ethical principles)
3. **Instantiate specific personas** with configurable characteristics
4. **Simulate interactions** that respect role-based ethical constraints
5. **Export personas** as semantic web artifacts (RDF/OWL)

### Current vs. Target State

| Aspect | Current A-Proxy | Integrated System |
|--------|-----------------|-------------------|
| Schema | Fixed 4-dimension model | Extensible ontology-driven |
| Roles | Implicit (occupation field) | Explicit role classes |
| Ethics | None | Full ethical framework |
| Export | JSON only | RDF/Turtle/JSON-LD |
| Interoperability | Isolated | MCP-connected ecosystem |

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           OntServe                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Ontology Storage & Querying (PostgreSQL + PLpgSQL)           │  │
│  │  - Persona Ontology (aproxy:Persona, aproxy:Role, etc.)       │  │
│  │  - Professional Domain Ontologies (Engineering, Teaching)     │  │
│  │  - Standard Ontologies (FOAF, Schema.org)                     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                    REST API / SPARQL                                 │
└──────────────────────────────┼───────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────────┐    ┌───────────────┐
│   A-Proxy     │    │     Proethica     │    │  Other MCP    │
│               │    │                   │    │   Clients     │
│ ┌───────────┐ │    │ ┌───────────────┐ │    │               │
│ │ Persona   │ │◄──►│ │ Ethical       │ │    │               │
│ │ Instanti- │ │    │ │ Decision      │ │    │               │
│ │ ation     │ │    │ │ Framework     │ │    │               │
│ └───────────┘ │    │ └───────────────┘ │    │               │
│               │    │                   │    │               │
│ ┌───────────┐ │    │ ┌───────────────┐ │    │               │
│ │ MCP       │◄────►│ │ Role-Based    │ │    │               │
│ │ Server    │ │    │ │ Ethics        │ │    │               │
│ └───────────┘ │    │ └───────────────┘ │    │               │
│               │    │                   │    │               │
│ ┌───────────┐ │    │ ┌───────────────┐ │    │               │
│ │ Journey   │ │    │ │ MCP Client    │ │    │               │
│ │ Tracking  │ │    │ └───────────────┘ │    │               │
│ └───────────┘ │    │                   │    │               │
└───────────────┘    └───────────────────┘    └───────────────┘
```

### Data Flow

1. **Role Import**: A-Proxy queries OntServe for role definitions
2. **Ethical Binding**: Proethica provides ethical constraints for roles
3. **Persona Creation**: A-Proxy instantiates persona from role template
4. **Simulation**: Claude AI responds as persona, respecting ethical framework
5. **Export**: Persona data can be exported back to OntServe as RDF

---

## Phase Implementation Plan

### Phase 1: Standalone Refactoring ✅ COMPLETE

- [x] Remove submodule dependencies
- [x] Implement repository pattern for database access
- [x] Create domain models as dataclasses
- [x] Simplify startup scripts
- [x] All tests passing

### Phase 2: Service Layer & Ontology Export

**Goal**: Add service layer abstraction and basic ontology export capability

```python
# services/persona_service.py
class PersonaService:
    def __init__(self, repository: PersonaRepository):
        self.repository = repository

    def create_persona(self, data: dict) -> Persona:
        """Create persona with validation."""
        pass

    def get_persona_context(self, persona_id: int) -> dict:
        """Get context suitable for LLM system prompts."""
        pass

    def export_to_ontology(self, persona_id: int, format: str) -> str:
        """Export persona as RDF/Turtle/JSON-LD."""
        pass
```

**New Files**:
```
services/
├── __init__.py
├── persona_service.py
└── context_service.py

ontology/
├── __init__.py
├── exporter.py          # Export personas to RDF
├── mappings.py          # Field-to-ontology mappings
└── namespaces.py        # RDF namespace definitions
```

**Deliverables**:
- PersonaService class
- RDF/Turtle export for personas
- JSON-LD export for personas
- Field-to-ontology mapping configuration

### Phase 3: MCP Server Implementation

**Goal**: Expose A-Proxy functionality via Model Context Protocol

```python
# mcp/server.py
class AProxyMCPServer:
    """MCP Server exposing persona operations."""

    def get_tools(self) -> list:
        return [
            {
                "name": "get_persona",
                "description": "Retrieve a persona by ID with all characteristics",
                "parameters": {
                    "persona_id": {"type": "integer", "required": True}
                }
            },
            {
                "name": "list_personas",
                "description": "List all personas with optional filtering",
                "parameters": {
                    "role_type": {"type": "string"},
                    "domain": {"type": "string"}
                }
            },
            {
                "name": "create_persona",
                "description": "Create a new persona",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "demographic": {"type": "object"},
                    "psychographic": {"type": "object"},
                    "behavioral": {"type": "object"},
                    "contextual": {"type": "object"}
                }
            },
            {
                "name": "create_persona_from_role",
                "description": "Create persona based on role definition from ontology",
                "parameters": {
                    "role_uri": {"type": "string", "required": True},
                    "customizations": {"type": "object"}
                }
            },
            {
                "name": "get_persona_ontology",
                "description": "Export persona as ontology format",
                "parameters": {
                    "persona_id": {"type": "integer", "required": True},
                    "format": {"type": "string", "enum": ["turtle", "jsonld", "rdfxml"]}
                }
            },
            {
                "name": "simulate_interaction",
                "description": "Simulate persona's response to a scenario",
                "parameters": {
                    "persona_id": {"type": "integer", "required": True},
                    "scenario": {"type": "string", "required": True},
                    "context": {"type": "object"}
                }
            }
        ]
```

**New Files**:
```
mcp/
├── __init__.py
├── server.py            # MCP server implementation
├── tools.py             # Tool definitions
└── handlers.py          # Request handlers
```

**Deliverables**:
- MCP server that can be started alongside Flask app
- Tool implementations for persona CRUD
- Tool implementations for ontology export
- Integration tests

### Phase 4: OntServe Client Integration

**Goal**: Enable A-Proxy to fetch role definitions from OntServe

```python
# mcp/ontserve_client.py
class OntServeClient:
    """MCP client for OntServe integration."""

    def __init__(self, ontserve_url: str):
        self.base_url = ontserve_url

    async def get_role_definition(self, role_uri: str) -> dict:
        """Fetch complete role definition from OntServe."""
        # Returns: competencies, ethical obligations, typical characteristics
        pass

    async def query_ontology(self, sparql_query: str) -> list:
        """Execute SPARQL query against OntServe."""
        pass

    async def get_professional_roles(self, domain: str) -> list:
        """Get all professional roles for a domain."""
        # domain: "engineering", "education", "healthcare", etc.
        pass

    async def get_role_hierarchy(self, role_uri: str) -> dict:
        """Get role inheritance hierarchy."""
        pass
```

**New Files**:
```
mcp/
├── ontserve_client.py   # OntServe MCP client
└── proethica_client.py  # Proethica MCP client
```

**Deliverables**:
- OntServe client with role fetching
- Role-to-persona mapping logic
- Caching layer for ontology data

### Phase 5: Proethica Integration & Professional Role Schema

**Goal**: Full integration with ethical decision-making framework

```python
# schemas/professional_role.py
PROFESSIONAL_ROLE_SCHEMA = {
    "role_identity": {
        "label": "Role Identity",
        "description": "Professional role characteristics",
        "fields": [
            {
                "name": "role_type",
                "type": "uri",
                "label": "Role Type",
                "description": "URI reference to role in ontology"
            },
            {
                "name": "domain",
                "type": "string",
                "label": "Professional Domain",
                "options": ["engineering", "education", "healthcare", "law", "finance"]
            },
            {
                "name": "specialization",
                "type": "string",
                "label": "Specialization"
            },
            {
                "name": "experience_level",
                "type": "string",
                "options": ["novice", "intermediate", "expert", "master"]
            },
            {
                "name": "certifications",
                "type": "list",
                "label": "Professional Certifications"
            }
        ]
    },
    "ethical_framework": {
        "label": "Ethical Framework",
        "description": "Ethical considerations for the role",
        "fields": [
            {
                "name": "ethical_principles",
                "type": "list",
                "label": "Core Ethical Principles",
                "description": "From proethica role definition"
            },
            {
                "name": "professional_codes",
                "type": "list",
                "label": "Professional Codes of Conduct"
            },
            {
                "name": "ethical_priorities",
                "type": "dict",
                "label": "Value Prioritization",
                "description": "How to prioritize competing values"
            },
            {
                "name": "decision_constraints",
                "type": "list",
                "label": "Decision Constraints"
            }
        ]
    },
    "competencies": {
        "label": "Professional Competencies",
        "description": "Skills and knowledge areas",
        "fields": [
            {
                "name": "technical_skills",
                "type": "list"
            },
            {
                "name": "soft_skills",
                "type": "list"
            },
            {
                "name": "knowledge_areas",
                "type": "list"
            },
            {
                "name": "decision_patterns",
                "type": "dict",
                "label": "Typical Decision Patterns"
            }
        ]
    }
}
```

**New Files**:
```
schemas/
├── __init__.py
├── base_persona.py          # Default persona schema
├── professional_role.py     # Professional role schema
└── schema_registry.py       # Dynamic schema loading

services/
└── persona_factory.py       # Create personas from role definitions
```

**Deliverables**:
- Professional role schema
- Persona factory for role-based creation
- Proethica client integration
- Ethical context injection for Claude prompts

---

## Ontology Design

### Core Classes

```turtle
@prefix aproxy: <http://example.org/a-proxy#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix schema: <http://schema.org/> .
@prefix proethica: <http://example.org/proethica#> .

# Core Persona Class
aproxy:Persona a owl:Class ;
    rdfs:label "Persona" ;
    rdfs:comment "An abstract representation of a person with specific characteristics" ;
    rdfs:subClassOf foaf:Person .

# Role Hierarchy
aproxy:Role a owl:Class ;
    rdfs:label "Role" ;
    rdfs:comment "A function or position that a persona can occupy" .

aproxy:ProfessionalRole a owl:Class ;
    rdfs:subClassOf aproxy:Role ;
    rdfs:label "Professional Role" .

aproxy:EngineerRole a owl:Class ;
    rdfs:subClassOf aproxy:ProfessionalRole ;
    rdfs:label "Engineer" .

aproxy:MechanicalEngineer a owl:Class ;
    rdfs:subClassOf aproxy:EngineerRole ;
    rdfs:label "Mechanical Engineer" .

aproxy:TeacherRole a owl:Class ;
    rdfs:subClassOf aproxy:ProfessionalRole ;
    rdfs:label "Teacher" .

# Characteristic Dimensions
aproxy:Characteristic a owl:Class .

aproxy:DemographicCharacteristic rdfs:subClassOf aproxy:Characteristic .
aproxy:PsychographicCharacteristic rdfs:subClassOf aproxy:Characteristic .
aproxy:BehavioralCharacteristic rdfs:subClassOf aproxy:Characteristic .
aproxy:ContextualCharacteristic rdfs:subClassOf aproxy:Characteristic .
aproxy:EthicalCharacteristic rdfs:subClassOf aproxy:Characteristic .
```

### Properties

```turtle
# Object Properties
aproxy:hasRole a owl:ObjectProperty ;
    rdfs:domain aproxy:Persona ;
    rdfs:range aproxy:Role .

aproxy:hasCharacteristic a owl:ObjectProperty ;
    rdfs:domain aproxy:Persona ;
    rdfs:range aproxy:Characteristic .

aproxy:requiresCompetency a owl:ObjectProperty ;
    rdfs:domain aproxy:Role ;
    rdfs:range aproxy:Competency .

aproxy:hasEthicalObligation a owl:ObjectProperty ;
    rdfs:domain aproxy:Role ;
    rdfs:range proethica:EthicalPrinciple .

aproxy:followsCode a owl:ObjectProperty ;
    rdfs:domain aproxy:Persona ;
    rdfs:range proethica:ProfessionalCode .

# Data Properties
aproxy:hasInterest a owl:DatatypeProperty ;
    rdfs:domain aproxy:Persona ;
    rdfs:range xsd:string .

aproxy:hasValue a owl:DatatypeProperty ;
    rdfs:domain aproxy:Persona ;
    rdfs:range xsd:string .

aproxy:hasExperienceLevel a owl:DatatypeProperty ;
    rdfs:domain aproxy:Persona ;
    rdfs:range xsd:string .
```

### Field Mappings

```python
# ontology/mappings.py
APROXY_TO_ONTOLOGY_MAPPING = {
    # A-Proxy field path -> Ontology property URI

    # Demographic mappings
    "demographic.occupation": "schema:jobTitle",
    "demographic.education": "schema:alumniOf",
    "demographic.age": "foaf:age",
    "demographic.location": "schema:location",
    "demographic.language": "schema:knowsLanguage",

    # Psychographic mappings
    "psychographic.interests": "foaf:interest",
    "psychographic.personal_values": "aproxy:hasValue",
    "psychographic.personality": "aproxy:personalityType",
    "psychographic.lifestyle": "aproxy:lifestyleType",

    # Behavioral mappings
    "behavioral.browsing_habits": "aproxy:hasBrowsingBehavior",
    "behavioral.device_usage": "aproxy:hasDevicePreference",
    "behavioral.social_media_activity": "aproxy:hasSocialMediaPresence",

    # Professional role mappings (for Proethica)
    "role.type": "rdf:type",
    "role.domain": "aproxy:hasProfessionalDomain",
    "role.specialization": "aproxy:hasSpecialization",
    "role.experience_level": "aproxy:hasExperienceLevel",
    "role.ethical_principles": "proethica:hasEthicalPrinciple",
    "role.professional_codes": "proethica:followsCode",
    "role.competencies": "aproxy:hasCompetency"
}
```

---

## MCP Integration

### A-Proxy as MCP Server

A-Proxy exposes these tools via MCP:

| Tool | Description | Use Case |
|------|-------------|----------|
| `get_persona` | Retrieve persona by ID | Display persona details |
| `list_personas` | List with filters | Browse personas by role |
| `create_persona` | Create from data | Manual persona creation |
| `create_persona_from_role` | Create from role URI | Role-based instantiation |
| `get_persona_ontology` | Export as RDF | Ontology integration |
| `simulate_interaction` | AI simulation | Training scenarios |

### A-Proxy as MCP Client

A-Proxy consumes these services:

| Service | Provider | Purpose |
|---------|----------|---------|
| Role definitions | OntServe | Get role templates |
| Ontology queries | OntServe | SPARQL lookups |
| Ethical frameworks | Proethica | Get ethical constraints |
| Professional codes | Proethica | Get code of conduct |

### Configuration

```python
# config.py additions
MCP_CONFIG = {
    "server": {
        "enabled": True,
        "port": 5003,
        "host": "127.0.0.1"
    },
    "clients": {
        "ontserve": {
            "url": "http://localhost:5050",
            "enabled": True
        },
        "proethica": {
            "url": "http://localhost:5060",
            "enabled": True
        }
    }
}
```

---

## Use Cases

### Use Case 1: Professional Ethics Training

**Scenario**: Training engineers to recognize and respond to ethical dilemmas

**Flow**:
```python
# 1. Import role from OntServe
role_def = await ontserve_client.get_role_definition(
    "proethica:MechanicalEngineer"
)

# 2. Get ethical framework from Proethica
ethics = await proethica_client.get_ethical_framework(
    role_uri="proethica:MechanicalEngineer",
    context="product_safety"
)

# 3. Create persona instance
engineer = await persona_factory.create_from_role(
    role_uri="proethica:MechanicalEngineer",
    overrides={
        "experience_level": "intermediate",
        "demographic": {"age": 35, "location": "Detroit, MI"},
        "ethical_focus": ["public_safety", "environmental_impact"]
    }
)

# 4. Simulate ethical dilemma
response = await persona_service.simulate_interaction(
    persona_id=engineer.id,
    scenario="""
        A senior manager requests you sign off on a component that
        meets minimum safety standards but not recommended best practices.
        Budget is tight and deadline is tomorrow.
    """,
    context={
        "ethical_framework": ethics,
        "response_format": "decision_with_reasoning"
    }
)

# 5. Track in journey
journey_id = journey_repo.save({
    "name": "Ethics Training - Safety Dilemma",
    "persona_id": engineer.id,
    "journey_type": "ethics_training"
})
```

### Use Case 2: Teacher Persona for Curriculum Development

**Scenario**: Model different teaching styles for curriculum testing

```python
# Create teaching personas with different approaches
teacher_types = [
    ("proethica:ElementaryTeacher", {"teaching_style": "constructivist"}),
    ("proethica:HighSchoolTeacher", {"teaching_style": "direct_instruction"}),
    ("proethica:SpecialEducationTeacher", {"teaching_style": "differentiated"})
]

for role_uri, overrides in teacher_types:
    teacher = await persona_factory.create_from_role(
        role_uri=role_uri,
        overrides={
            "domain": "mathematics",
            **overrides
        }
    )

    # Test curriculum response
    response = await persona_service.simulate_interaction(
        persona_id=teacher.id,
        scenario="Evaluate this lesson plan for teaching fractions to 4th graders",
        context={"lesson_plan": lesson_plan_content}
    )
```

### Use Case 3: Ontology-Driven Market Research

**Scenario**: Create consumer personas based on market segment ontology

```python
# Query OntServe for consumer segment roles
segments = await ontserve_client.query_ontology("""
    SELECT ?segment ?label WHERE {
        ?segment rdfs:subClassOf marketing:ConsumerSegment .
        ?segment rdfs:label ?label .
    }
""")

# Create personas for each segment
for segment in segments:
    persona = await persona_factory.create_from_role(
        role_uri=segment['segment'],
        overrides={
            "behavioral": {
                "purchase_frequency": "high" if "premium" in segment['label'] else "moderate"
            }
        }
    )

    # Export to ontology for analysis
    rdf_data = persona_service.export_to_ontology(
        persona_id=persona.id,
        format="turtle"
    )

    # Submit to OntServe for storage
    await ontserve_client.store_instance(rdf_data)
```

---

## Technical Specifications

### Database Schema Extensions

```sql
-- New table for role associations
CREATE TABLE persona_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id INTEGER NOT NULL,
    role_uri TEXT NOT NULL,
    role_source TEXT DEFAULT 'ontserve',  -- 'ontserve', 'proethica', 'local'
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
);

-- New table for ethical framework associations
CREATE TABLE persona_ethics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    persona_id INTEGER NOT NULL,
    framework_uri TEXT NOT NULL,
    principles TEXT,  -- JSON array of principle URIs
    codes TEXT,       -- JSON array of code URIs
    priorities TEXT,  -- JSON object of priority rankings
    FOREIGN KEY (persona_id) REFERENCES personas (id) ON DELETE CASCADE
);
```

### API Additions

```python
# New REST endpoints
@app.route('/api/v1/personas/<id>/ontology', methods=['GET'])
def get_persona_ontology(id):
    """Export persona as RDF."""
    format = request.args.get('format', 'turtle')
    return persona_service.export_to_ontology(id, format)

@app.route('/api/v1/personas/from-role', methods=['POST'])
def create_from_role():
    """Create persona from ontology role."""
    data = request.json
    return persona_factory.create_from_role(
        role_uri=data['role_uri'],
        overrides=data.get('overrides', {})
    )

@app.route('/api/v1/roles', methods=['GET'])
def list_roles():
    """List available roles from OntServe."""
    domain = request.args.get('domain')
    return ontserve_client.get_professional_roles(domain)
```

### Dependencies

```
# requirements.txt additions
rdflib>=6.0.0          # RDF/OWL handling
SPARQLWrapper>=2.0.0   # SPARQL queries
mcp>=0.1.0             # Model Context Protocol
pydantic>=2.0.0        # Data validation
```

---

## Timeline Estimates

| Phase | Scope | Complexity |
|-------|-------|------------|
| Phase 1 | Standalone refactoring | ✅ Complete |
| Phase 2 | Service layer + ontology export | Medium |
| Phase 3 | MCP server | Medium |
| Phase 4 | OntServe client | Medium-High |
| Phase 5 | Proethica integration | High |

## Repository Links

- **A-Proxy**: This repository
- **OntServe**: https://github.com/MatLab-Research/OntServe
- **Proethica**: https://github.com/cr625/proethica

---

## Next Steps

1. Review this integration plan
2. Prioritize phases based on project needs
3. Begin Phase 2 implementation (service layer)
4. Coordinate with OntServe/Proethica teams on API contracts
