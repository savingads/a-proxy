# Persona MCP Server

A Model Context Protocol (MCP) server that provides access to the Persona API service. This allows chat models and language models to interact with personas using the MCP protocol while preserving the existing API architecture.

## Overview

This MCP server acts as a sidecar that connects to your existing Persona REST API, exposing its functionality through the Model Context Protocol. This approach allows:

1. Chat models and LLMs to access persona data via MCP tools and resources
2. External applications to use either the REST API or MCP interface
3. Preservation of your existing application architecture

## Features

- **MCP Resources** - Access personas and schema information via URI-based resources
- **MCP Tools** - Perform operations on personas via MCP tools
- **Integration with Existing API** - Seamlessly connects to your existing Persona API service
- **No Modifications to Existing Code** - Works alongside your current application without changing it

## Installation

1. Build the MCP server:

```bash
cd persona-mcp-server
npm install
npm run build
```

2. Configure the MCP server in your MCP settings file:

```json
{
  "mcpServers": {
    "persona": {
      "command": "node",
      "args": ["/path/to/persona-mcp-server/dist/index.js"],
      "env": {
        "PERSONA_API_URL": "http://localhost:5050/api/v1"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## Environment Variables

- `PERSONA_API_URL` - The base URL for the Persona API (default: `http://localhost:5050/api/v1`)

## Available MCP Resources

- `persona://schema` - JSON schema definition for persona objects
- `persona://{id}` - Access a specific persona by ID

## Available MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_personas` | Get a list of all personas | `page`, `per_page` |
| `get_persona` | Get a specific persona | `id` (required) |
| `create_persona` | Create a new persona | `name` (required), `demographic`, `psychographic`, `behavioral`, `contextual` |
| `update_persona` | Update an existing persona | `id` (required), `name`, `demographic`, `psychographic`, `behavioral`, `contextual` |
| `delete_persona` | Delete a persona | `id` (required) |
| `get_field_config` | Get field configuration | `category`, `field` |

## MCP Client Example (TypeScript)

```typescript
import { Client } from '@modelcontextprotocol/sdk/client';
import { SocketClientTransport } from '@modelcontextprotocol/sdk/client/socket';

async function main() {
  // Connect to the MCP server
  const transport = new SocketClientTransport('localhost', 8123);
  const client = new Client();
  await client.connect(transport);
  
  // List all personas
  const response = await client.callTool('persona-server', 'list_personas', {
    page: 1,
    per_page: 10
  });
  
  console.log(JSON.parse(response.content[0].text));
  
  // Get a specific persona
  const persona = await client.callTool('persona-server', 'get_persona', {
    id: 1
  });
  
  console.log(JSON.parse(persona.content[0].text));
}

main().catch(console.error);
```

## Benefits of This Approach

- **Zero Disruption** - Your current application architecture remains unchanged
- **Multiple Access Methods** - Support for both REST API and MCP protocols 
- **Incremental Adoption** - Gradually adopt MCP features as needed
- **LLM Integration** - Enable rich interaction between language models and your personas
- **External Application Support** - Other applications can use either interface
