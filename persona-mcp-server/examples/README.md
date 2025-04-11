# Persona MCP Client Examples

This directory contains example code demonstrating how to interact with the Persona MCP Server from external applications.

## Prerequisites

- Node.js 16+ installed
- Persona API Service running (http://localhost:5050)
- Persona MCP Server running

## Setup

Install the dependencies for the examples:

```bash
cd examples
npm install
```

## Running the Examples

### Note About TypeScript Example

The TypeScript example (`mcp-client-example.ts`) is provided as a reference for TypeScript users. However, there are currently some compatibility issues between the TypeScript type definitions and the actual MCP SDK structure in version 1.9.0. 

### JavaScript Example (Recommended)

We recommend using the JavaScript version of the example instead:

```bash
npm run start:js
```

**Note**: If you still encounter errors with the JavaScript example, it might be due to how the MCP SDK package exports its modules. The examples assume a specific package structure which may vary by SDK version.

### Example Functionality

The examples demonstrate how to:

- Connect to the MCP server
- Access resources (schema, personas)
- List personas
- Create a persona
- Update a persona
- Delete a persona

### Expected Output

When running successfully, you should see output similar to this:

```
Connecting to MCP server...
Connected to MCP server successfully!

Accessing resource: persona://schema

Resource content:
{
  "type": "object",
  "properties": {
    "id": { "type": "integer" },
    "name": { "type": "string" },
    ...
  }
}

Calling tool: list_personas with args: { page: 1, per_page: 5 }

Tool result:
{
  "personas": [...],
  "total": 10,
  "page": 1,
  "per_page": 5
}

...

Persona operations completed successfully!

Disconnected from MCP server
```

## Troubleshooting

If you encounter errors:

1. **Connection errors**: Ensure the MCP server is running
2. **Missing personas**: Verify the Persona API service is running and has data
3. **Import errors**: Check if the installed SDK version matches the import paths

## Configuration

You can modify these settings in the example code:

- **Host**: Default is `localhost`
- **Port**: Default is `8123`
- **Server name**: Default is `persona-server`
