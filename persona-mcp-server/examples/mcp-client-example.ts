/**
 * Example MCP client for the Persona MCP Server
 *
 * This example shows how an external application could use MCP to interact with personas.
 * To run this example:
 * 1. Make sure the Persona API service is running
 * 2. Make sure the Persona MCP Server is configured and running
 * 3. Install dependencies: cd examples && npm install
 * 4. Run: npm start
 */

// Import directly from the SDK main package
// The examples directory uses CommonJS format (type: "commonjs" in package.json)
const { Client, SocketClientTransport } = require('@modelcontextprotocol/sdk');

// Function to access a resource
async function accessResource(client: any, uri: string) {
  console.log(`\nAccessing resource: ${uri}`);
  try {
    const result = await client.readResource('persona-server', uri);
    if (result.contents && result.contents.length > 0) {
      const content = result.contents[0].text;
      console.log(`\nResource content:\n${content}`);
      return JSON.parse(content);
    }
  } catch (error) {
    console.error(`Error accessing resource ${uri}:`, error);
  }
  return null;
}

// Function to call a tool
async function callTool(client: any, toolName: string, args: any) {
  console.log(`\nCalling tool: ${toolName} with args:`, args);
  try {
    const result = await client.callTool('persona-server', toolName, args);
    if (result.content && result.content.length > 0) {
      const content = result.content[0].text;
      console.log(`\nTool result:\n${content}`);
      return JSON.parse(content);
    }
  } catch (error) {
    console.error(`Error calling tool ${toolName}:`, error);
  }
  return null;
}

// Main function
async function main() {
  console.log('Connecting to MCP server...');

  // In a real application, you would configure these values
  const host = 'localhost';
  const port = 8123; // Default MCP port

  // Connect to the MCP server
  const transport = new SocketClientTransport(host, port);
  const client = new Client();

  try {
    await client.connect(transport);
    console.log('Connected to MCP server successfully!');

    // Get the persona schema
    const schema = await accessResource(client, 'persona://schema');

    // List all personas
    const personaList = await callTool(client, 'list_personas', {
      page: 1,
      per_page: 5
    });

    if (personaList && personaList.personas && personaList.personas.length > 0) {
      // Get the first persona
      const firstPersonaId = personaList.personas[0].id;
      console.log(`\nAccessing first persona with ID: ${firstPersonaId}`);

      // Get the persona by ID using resource
      const personaResource = await accessResource(client, `persona://${firstPersonaId}`);

      // Get the persona by ID using tool
      const personaTool = await callTool(client, 'get_persona', { id: firstPersonaId });

      // Create a new persona
      const newPersona = await callTool(client, 'create_persona', {
        name: 'MCP Created Persona',
        demographic: {
          country: 'United States',
          city: 'San Francisco',
          age: 30
        },
        psychographic: {
          interests: ['technology', 'AI', 'programming']
        }
      });

      if (newPersona && newPersona.id) {
        // Update the persona
        await callTool(client, 'update_persona', {
          id: newPersona.id,
          psychographic: {
            interests: ['technology', 'AI', 'programming', 'MCP']
          }
        });

        // Retrieve the updated persona
        await callTool(client, 'get_persona', { id: newPersona.id });

        // Delete the persona
        await callTool(client, 'delete_persona', { id: newPersona.id });

        console.log('\nPersona operations completed successfully!');
      }
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    // Close the connection
    await client.disconnect();
    console.log('\nDisconnected from MCP server');
  }
}

// Run the example
main().catch(console.error);
