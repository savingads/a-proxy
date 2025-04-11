# Persona Service Integration Guide

This guide explains how to integrate the Persona Service into your applications, either directly through its REST API or through an MCP server for AI assistant integration.

## Option 1: Direct API Integration

The simplest way to integrate with the Persona Service is to make HTTP requests directly to its REST API endpoints.

### Authentication (if enabled)

```python
import requests

def get_auth_token(base_url, username, password):
    """Get an authentication token from the Persona Service"""
    auth_url = f"{base_url}/api/v1/auth/login"
    response = requests.post(auth_url, json={
        "username": username,
        "password": password
    })
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        raise Exception(f"Authentication failed: {response.text}")

# Usage
base_url = "http://localhost:5050"
token = get_auth_token(base_url, "admin", "your_password")
headers = {"Authorization": f"Bearer {token}"}
```

### Working with Personas

```python
import requests

class PersonaServiceClient:
    """Simple client for the Persona Service API"""
    
    def __init__(self, base_url="http://localhost:5050", token=None):
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1"
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def get_personas(self, page=1, per_page=20):
        """Get all personas with pagination"""
        url = f"{self.api_url}/personas"
        params = {"page": page, "per_page": per_page}
        response = requests.get(url, params=params, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get personas: {response.text}")
    
    def get_persona(self, persona_id):
        """Get a specific persona by ID"""
        url = f"{self.api_url}/personas/{persona_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get persona {persona_id}: {response.text}")
    
    def create_persona(self, persona_data):
        """Create a new persona"""
        url = f"{self.api_url}/personas"
        response = requests.post(url, json=persona_data, headers=self.headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create persona: {response.text}")
    
    def update_persona(self, persona_id, persona_data):
        """Update an existing persona"""
        url = f"{self.api_url}/personas/{persona_id}"
        response = requests.put(url, json=persona_data, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to update persona {persona_id}: {response.text}")
    
    def delete_persona(self, persona_id):
        """Delete a persona"""
        url = f"{self.api_url}/personas/{persona_id}"
        response = requests.delete(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to delete persona {persona_id}: {response.text}")
    
    def get_demographic_data(self, persona_id):
        """Get demographic data for a persona"""
        url = f"{self.api_url}/personas/{persona_id}/demographic"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get demographic data for persona {persona_id}: {response.text}")
    
    def update_demographic_data(self, persona_id, demographic_data):
        """Update demographic data for a persona"""
        url = f"{self.api_url}/personas/{persona_id}/demographic"
        response = requests.put(url, json=demographic_data, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to update demographic data for persona {persona_id}: {response.text}")

# Usage example
client = PersonaServiceClient("http://localhost:5050")
personas = client.get_personas()
print(f"Found {len(personas['personas'])} personas")

# Create a new persona
new_persona = client.create_persona({
    "name": "Example User",
    "demographic": {
        "country": "US",
        "city": "San Francisco",
        "language": "en-US"
    },
    "psychographic": {
        "interests": ["technology", "travel", "cooking"]
    }
})
print(f"Created persona with ID: {new_persona['id']}")
```

### Integration in a Flask Application

Here's how to integrate the Persona Service in a Flask application:

```python
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Persona Service configuration
PERSONA_SERVICE_URL = "http://localhost:5050"

def get_persona_client():
    """Get a configured Persona Service client"""
    from your_app.services import PersonaServiceClient
    return PersonaServiceClient(PERSONA_SERVICE_URL)

@app.route('/personas')
def list_personas():
    """Display personas in a web page"""
    client = get_persona_client()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        result = client.get_personas(page=page, per_page=per_page)
        return render_template('personas.html', personas=result['personas'])
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/api/personas')
def api_list_personas():
    """API endpoint that proxies to the Persona Service"""
    client = get_persona_client()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        result = client.get_personas(page=page, per_page=per_page)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## Option 2: Python Client Library

For Python applications, you can use the persona-client library:

```bash
pip install persona-client
```

```python
from personaclient import PersonaClient

# Initialize the client
client = PersonaClient(
    base_url="http://localhost:5050",
    api_version="v1",
    timeout=10,
    auth_token=None  # Optional authentication token
)

# Get all personas with pagination
personas = client.get_all_personas(page=1, per_page=20)
print(f"Found {len(personas['personas'])} personas")

# Get a specific persona
persona = client.get_persona(1)
print(f"Retrieved persona: {persona['name']}")

# Create a new persona
new_persona = client.create_persona({
    "name": "Test User",
    "demographic": {
        "country": "Canada",
        "city": "Toronto",
        "language": "en-CA"
    }
})
print(f"Created persona with ID: {new_persona['id']}")

# Update psychographic data
client.update_psychographic_data(new_persona['id'], {
    "interests": ["technology", "music", "hiking"]
})
```

## Option 3: MCP Integration

For AI assistant integration using the Model Context Protocol (MCP), you can create an MCP server that connects to the Persona Service.

### Example MCP Server Implementation

Here's a simplified example of how to create an MCP server that exposes Persona Service functionality:

```typescript
// persona-mcp-server.ts
import { Server } from '@modelcontextprotocol/sdk/server';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio';
import axios from 'axios';

const PERSONA_API_URL = process.env.PERSONA_API_URL || 'http://localhost:5050/api/v1';

class PersonaMcpServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: 'persona-server',
        version: '0.1.0',
      },
      {
        capabilities: {
          resources: {},
          tools: {},
        },
      }
    );

    this.setupResourceHandlers();
    this.setupToolHandlers();
    
    // Error handling
    this.server.onerror = (error) => console.error('[MCP Error]', error);
  }

  private setupResourceHandlers() {
    // List resources (schema and personas by ID)
    this.server.setRequestHandler('list_resources', async () => ({
      resources: [
        {
          uri: `persona://schema`,
          name: `Persona Schema`,
          mimeType: 'application/json',
          description: 'Schema definition for persona data structure',
        },
      ],
    }));

    // Setup resource templates (dynamic resources)
    this.server.setRequestHandler('list_resource_templates', async () => ({
      resourceTemplates: [
        {
          uriTemplate: 'persona://{id}',
          name: 'Persona by ID',
          mimeType: 'application/json',
          description: 'Get a specific persona by ID',
        },
      ],
    }));

    // Resource handler
    this.server.setRequestHandler('read_resource', async (request) => {
      const uri = request.params.uri;
      
      // Handle persona schema resource
      if (uri === 'persona://schema') {
        try {
          const response = await axios.get(`${PERSONA_API_URL}/schema`);
          return {
            contents: [
              {
                uri,
                mimeType: 'application/json',
                text: JSON.stringify(response.data, null, 2),
              },
            ],
          };
        } catch (error) {
          console.error('Error fetching schema:', error);
          throw new Error(`Failed to fetch schema: ${error.message}`);
        }
      }
      
      // Handle persona by ID
      const match = uri.match(/^persona:\/\/(\d+)$/);
      if (match) {
        const personaId = match[1];
        try {
          const response = await axios.get(`${PERSONA_API_URL}/personas/${personaId}`);
          return {
            contents: [
              {
                uri,
                mimeType: 'application/json',
                text: JSON.stringify(response.data, null, 2),
              },
            ],
          };
        } catch (error) {
          console.error(`Error fetching persona ${personaId}:`, error);
          throw new Error(`Failed to fetch persona ${personaId}: ${error.message}`);
        }
      }
      
      throw new Error(`Unsupported resource URI: ${uri}`);
    });
  }

  private setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler('list_tools', async () => ({
      tools: [
        {
          name: 'list_personas',
          description: 'Get a list of personas with pagination',
          inputSchema: {
            type: 'object',
            properties: {
              page: { type: 'number', description: 'Page number' },
              per_page: { type: 'number', description: 'Items per page' },
            },
          },
        },
        {
          name: 'get_persona',
          description: 'Get a specific persona by ID',
          inputSchema: {
            type: 'object',
            properties: {
              id: { type: 'number', description: 'Persona ID' },
            },
            required: ['id'],
          },
        },
        {
          name: 'create_persona',
          description: 'Create a new persona',
          inputSchema: {
            type: 'object',
            properties: {
              name: { type: 'string', description: 'Persona name' },
              demographic: { 
                type: 'object',
                description: 'Demographic information' 
              },
              psychographic: { 
                type: 'object',
                description: 'Psychographic information' 
              },
            },
            required: ['name'],
          },
        },
        {
          name: 'update_persona',
          description: 'Update an existing persona',
          inputSchema: {
            type: 'object',
            properties: {
              id: { type: 'number', description: 'Persona ID' },
              name: { type: 'string', description: 'Persona name' },
              demographic: { 
                type: 'object',
                description: 'Demographic information' 
              },
              psychographic: { 
                type: 'object',
                description: 'Psychographic information' 
              },
            },
            required: ['id'],
          },
        },
        {
          name: 'delete_persona',
          description: 'Delete a persona',
          inputSchema: {
            type: 'object',
            properties: {
              id: { type: 'number', description: 'Persona ID' },
            },
            required: ['id'],
          },
        },
      ],
    }));

    // Tool handler
    this.server.setRequestHandler('call_tool', async (request) => {
      const toolName = request.params.name;
      const args = request.params.arguments;

      try {
        let result;
        
        switch (toolName) {
          case 'list_personas':
            const page = args.page || 1;
            const perPage = args.per_page || 20;
            const response = await axios.get(`${PERSONA_API_URL}/personas`, {
              params: { page, per_page: perPage },
            });
            result = response.data;
            break;
            
          case 'get_persona':
            if (!args.id) throw new Error('Missing required parameter: id');
            const getResponse = await axios.get(`${PERSONA_API_URL}/personas/${args.id}`);
            result = getResponse.data;
            break;
            
          case 'create_persona':
            if (!args.name) throw new Error('Missing required parameter: name');
            const createResponse = await axios.post(`${PERSONA_API_URL}/personas`, args);
            result = createResponse.data;
            break;
            
          case 'update_persona':
            if (!args.id) throw new Error('Missing required parameter: id');
            const updateResponse = await axios.put(`${PERSONA_API_URL}/personas/${args.id}`, args);
            result = updateResponse.data;
            break;
            
          case 'delete_persona':
            if (!args.id) throw new Error('Missing required parameter: id');
            const deleteResponse = await axios.delete(`${PERSONA_API_URL}/personas/${args.id}`);
            result = deleteResponse.data;
            break;
            
          default:
            throw new Error(`Unknown tool: ${toolName}`);
        }

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (error) {
        console.error(`Error calling tool ${toolName}:`, error);
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Persona MCP server running on stdio');
  }
}

const server = new PersonaMcpServer();
server.run().catch(console.error);
```

### Using the MCP Server

Once you have the MCP server running, you can configure it in your AI assistant platform (like Claude Desktop or Claude Developer) and use it to interact with personas.

### MCP Client Example

```typescript
import { Client, SocketClientTransport } from '@modelcontextprotocol/sdk';

async function main() {
  // Connect to the MCP server
  const transport = new SocketClientTransport('localhost', 8123);
  const client = new Client();
  
  await client.connect(transport);
  console.log('Connected to MCP server');
  
  try {
    // List all personas
    const personaList = await client.callTool('persona-server', 'list_personas', {
      page: 1,
      per_page: 5
    });
    
    console.log('Personas:', JSON.parse(personaList.content[0].text));
    
    // Get a specific persona
    const firstPersona = JSON.parse(personaList.content[0].text).personas[0];
    if (firstPersona) {
      const personaDetail = await client.callTool('persona-server', 'get_persona', {
        id: firstPersona.id
      });
      
      console.log('Persona details:', JSON.parse(personaDetail.content[0].text));
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await client.disconnect();
    console.log('Disconnected from MCP server');
  }
}

main().catch(console.error);
```

## Integration Considerations

### Error Handling

All integration approaches should include proper error handling:

```python
try:
    result = client.get_persona(persona_id)
    # Process the result
except Exception as e:
    # Handle the error appropriately
    print(f"Error getting persona: {e}")
    # Log the error, show a user-friendly message, etc.
```

### Caching

Consider implementing caching for frequently accessed persona data:

```python
import functools
from datetime import datetime, timedelta

# Simple in-memory cache with expiration
cache = {}

def cached(expiration_seconds=300):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check if we have a valid cached result
            if key in cache:
                timestamp, result = cache[key]
                if datetime.now() - timestamp < timedelta(seconds=expiration_seconds):
                    return result
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache[key] = (datetime.now(), result)
            return result
        return wrapper
    return decorator

# Usage example
@cached(expiration_seconds=60)
def get_personas(client, page=1, per_page=20):
    return client.get_personas(page=page, per_page=per_page)
```

### Connection Pooling

For applications with high request volumes, implement connection pooling:

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_http_session():
    """Get a configured HTTP session with connection pooling and retries"""
    session = requests.Session()
    
    # Configure connection pooling
    adapter = HTTPAdapter(
        pool_connections=10,
        pool_maxsize=20,
        max_retries=Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
    )
    
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session

# Usage
def get_persona_client():
    session = get_http_session()
    return PersonaServiceClient(
        base_url="http://localhost:5050",
        session=session
    )
```

### Resilience and Circuit Breaking

For production systems, implement circuit breaking to prevent cascading failures:

```python
from pybreaker import CircuitBreaker

# Create a circuit breaker
persona_breaker = CircuitBreaker(
    fail_max=5,           # Number of failures before opening the circuit
    reset_timeout=60,     # Seconds until attempting to close the circuit
    exclude=[RequestException]  # Exceptions that shouldn't count as failures
)

# Apply circuit breaker to API call
@persona_breaker
def get_persona(client, persona_id):
    return client.get_persona(persona_id)

# Usage with error handling
try:
    persona = get_persona(client, 1)
    # Process the persona
except CircuitBreakerError:
    # Circuit is open due to too many failures
    print("Persona service is currently unavailable")
    # Use a fallback mechanism or show appropriate error
```

## Security Considerations

### Authentication

If your Persona Service has authentication enabled:

1. Store authentication tokens securely
2. Implement token refresh logic
3. Use HTTPS for all API communications
4. Consider using environment variables for sensitive credentials

### Data Protection

When working with persona data:

1. Validate all input data before sending to the API
2. Implement access controls for who can view or modify persona data
3. Consider data retention policies for persona information
4. Be aware of relevant privacy regulations (GDPR, CCPA, etc.)
