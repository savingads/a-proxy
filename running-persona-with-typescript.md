# Running Persona Service & MCP Client Without Docker

This guide explains how to run the Persona Service API and MCP TypeScript client without Docker.

## TypeScript Fix

The MCP client example in `persona-mcp-server/examples/mcp-client-example.ts` was using ES Module import syntax while the project was configured for CommonJS. The fix was to use `require()` instead of `import`:

```typescript
// The examples directory uses CommonJS format (type: "commonjs" in package.json)
const { Client, SocketClientTransport } = require('@modelcontextprotocol/sdk');
```

## Running the Development Environment

Two separate scripts have been created to make it easier to run the services:

### 1. Run Persona Service API

To run just the Persona Service API:

```bash
./run-persona-service.sh
```

This script:
- Creates a Python virtual environment if needed
- Installs all required Python dependencies (from requirements.txt)
- Installs additional required dependencies:
  - flask-sqlalchemy
  - flask-marshmallow
  - marshmallow-sqlalchemy
- Starts the Persona Service API on port 5050 in debug mode

### 2. Run MCP Client Example

To run just the MCP client TypeScript example:

```bash
./run-mcp-client.sh
```

This script:
- Sets up the MCP client environment with npm
- Runs the TypeScript example using ts-node

**Note:** Make sure the Persona Service API is running first (in a separate terminal) before running the MCP client example.

## Common Issues Fixed

Several issues were fixed to make the system run without Docker:

1. **Missing Python Dependencies**
   - Added missing dependencies that weren't in requirements.txt

2. **Module Import Fixes**
   - Fixed circular import by changing `from app.__init__ import db` to `from app.extensions import db`
   - Fixed blueprint name (from `api_blueprint` to `api_bp`)

3. **Syntax Error Fixes**
   - Added missing commas in function arguments
   - Fixed incorrect quotes and string formatting
   - Cleaned up route declarations

## Development Workflow

1. Start the Persona Service in one terminal:
   ```bash
   ./run-persona-service.sh
   ```

2. In another terminal, run the MCP client:
   ```bash
   ./run-mcp-client.sh
   ```

This workflow allows you to test the MCP client against a local running instance of the Persona Service.
