#!/usr/bin/env node
import axios from 'axios';

// Configuration accessed from environment variables
const API_BASE_URL = process.env.PERSONA_API_URL || 'http://localhost:5050/api/v1';

/**
 * MCP Server that acts as a bridge to the Persona REST API
 */
class PersonaMcpServer {
  private server: any;
  private apiClient: any;

  constructor() {
    // Dynamically import the MCP SDK to avoid TypeScript issues
    const mcp = require('@modelcontextprotocol/sdk');
    
    // Initialize the MCP server
    this.server = new mcp.Server(
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

    // Create API client that connects to the existing REST API
    this.apiClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 5000,
    });

    // Set up MCP handlers
    this.setupResourceHandlers(mcp);
    this.setupToolHandlers(mcp);
    
    // Error handling
    this.server.onerror = (error: any) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  /**
   * Set up handlers for MCP resources
   */
  private setupResourceHandlers(mcp: any) {
    // List available resources
    this.server.setRequestHandler(mcp.ListResourcesRequestSchema, async () => ({
      resources: [
        {
          uri: 'persona://schema',
          name: 'Persona Schema',
          mimeType: 'application/json',
          description: 'Schema definition for persona objects',
        }
      ],
    }));

    // Define resource templates for accessing personas by ID
    this.server.setRequestHandler(
      mcp.ListResourceTemplatesRequestSchema,
      async () => ({
        resourceTemplates: [
          {
            uriTemplate: 'persona://{id}',
            name: 'Individual persona by ID',
            mimeType: 'application/json',
            description: 'Access a specific persona by its ID',
          }
        ],
      })
    );

    // Handle resource requests
    this.server.setRequestHandler(
      mcp.ReadResourceRequestSchema,
      async (request: any) => {
        // Special case for schema
        if (request.params.uri === 'persona://schema') {
          return {
            contents: [
              {
                uri: request.params.uri,
                mimeType: 'application/json',
                text: JSON.stringify({
                  type: 'object',
                  properties: {
                    id: { type: 'integer' },
                    name: { type: 'string' },
                    demographic: {
                      type: 'object',
                      properties: {
                        latitude: { type: 'number' },
                        longitude: { type: 'number' },
                        language: { type: 'string' },
                        country: { type: 'string' },
                        city: { type: 'string' },
                        region: { type: 'string' },
                        age: { type: 'integer' },
                        gender: { type: 'string' },
                        education: { type: 'string' },
                        income: { type: 'string' },
                        occupation: { type: 'string' }
                      }
                    },
                    psychographic: {
                      type: 'object',
                      properties: {
                        interests: { type: 'array', items: { type: 'string' } },
                        personal_values: { type: 'array', items: { type: 'string' } },
                        attitudes: { type: 'array', items: { type: 'string' } },
                        lifestyle: { type: 'string' },
                        personality: { type: 'string' },
                        opinions: { type: 'array', items: { type: 'string' } }
                      }
                    },
                    behavioral: {
                      type: 'object',
                      properties: {
                        browsing_habits: { type: 'array', items: { type: 'string' } },
                        purchase_history: { type: 'array', items: { type: 'string' } },
                        brand_interactions: { type: 'array', items: { type: 'string' } },
                        device_usage: { type: 'object' },
                        social_media_activity: { type: 'object' },
                        content_consumption: { type: 'object' }
                      }
                    },
                    contextual: {
                      type: 'object',
                      properties: {
                        time_of_day: { type: 'string' },
                        day_of_week: { type: 'string' },
                        season: { type: 'string' },
                        weather: { type: 'string' },
                        device_type: { type: 'string' },
                        browser_type: { type: 'string' },
                        screen_size: { type: 'string' },
                        connection_type: { type: 'string' }
                      }
                    }
                  },
                  required: ['name']
                }, null, 2),
              },
            ],
          };
        }

        // Handle persona ID resources
        const match = request.params.uri.match(/^persona:\/\/(\d+)$/);
        if (!match) {
          throw new mcp.McpError(
            mcp.ErrorCode.InvalidRequest,
            `Invalid URI format: ${request.params.uri}`
          );
        }
        
        const personaId = match[1];
        
        try {
          const response = await this.apiClient.get(`/personas/${personaId}`);
          
          return {
            contents: [
              {
                uri: request.params.uri,
                mimeType: 'application/json',
                text: JSON.stringify(response.data, null, 2),
              },
            ],
          };
        } catch (error: any) {
          if (axios.isAxiosError(error)) {
            if (error.response?.status === 404) {
              throw new mcp.McpError(
                mcp.ErrorCode.NotFound,
                `Persona with ID ${personaId} not found`
              );
            }
          }
          throw new mcp.McpError(
            mcp.ErrorCode.InternalError,
            `Error fetching persona: ${error.message || String(error)}`
          );
        }
      }
    );
  }

  /**
   * Set up handlers for MCP tools
   */
  private setupToolHandlers(mcp: any) {
    // Define tools that map to API operations
    this.server.setRequestHandler(mcp.ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'list_personas',
          description: 'Get a list of all personas with optional pagination',
          inputSchema: {
            type: 'object',
            properties: {
              page: {
                type: 'number',
                description: 'Page number (starts at 1)',
              },
              per_page: {
                type: 'number',
                description: 'Number of items per page',
              },
            },
          },
        },
        {
          name: 'get_persona',
          description: 'Get a specific persona by ID',
          inputSchema: {
            type: 'object',
            properties: {
              id: {
                type: 'number',
                description: 'Persona ID',
              },
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
              name: {
                type: 'string',
                description: 'Persona name',
              },
              demographic: {
                type: 'object',
                description: 'Demographic data',
              },
              psychographic: {
                type: 'object',
                description: 'Psychographic data',
              },
              behavioral: {
                type: 'object',
                description: 'Behavioral data',
              },
              contextual: {
                type: 'object',
                description: 'Contextual data',
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
              id: {
                type: 'number',
                description: 'Persona ID',
              },
              name: {
                type: 'string',
                description: 'Persona name',
              },
              demographic: {
                type: 'object',
                description: 'Demographic data',
              },
              psychographic: {
                type: 'object',
                description: 'Psychographic data',
              },
              behavioral: {
                type: 'object',
                description: 'Behavioral data',
              },
              contextual: {
                type: 'object',
                description: 'Contextual data',
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
              id: {
                type: 'number',
                description: 'Persona ID',
              },
            },
            required: ['id'],
          },
        },
        {
          name: 'get_field_config',
          description: 'Get field configuration',
          inputSchema: {
            type: 'object',
            properties: {
              category: {
                type: 'string',
                description: 'Category name (optional)',
              },
              field: {
                type: 'string',
                description: 'Field name (optional)',
              },
            },
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(mcp.CallToolRequestSchema, async (request: any) => {
      try {
        switch (request.params.name) {
          case 'list_personas': {
            const { page, per_page } = request.params.arguments || {};
            const response = await this.apiClient.get('/personas', {
              params: { page, per_page }
            });
            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(response.data, null, 2),
                },
              ],
            };
          }
          
          case 'get_persona': {
            const { id } = request.params.arguments || {};
            if (!id) {
              return {
                content: [{ type: 'text', text: 'Error: Persona ID is required' }],
                isError: true,
              };
            }
            
            const response = await this.apiClient.get(`/personas/${id}`);
            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(response.data, null, 2),
                },
              ],
            };
          }
          
          case 'create_persona': {
            const personaData = request.params.arguments;
            const response = await this.apiClient.post('/personas', personaData);
            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(response.data, null, 2),
                },
              ],
            };
          }
          
          case 'update_persona': {
            const { id, ...personaData } = request.params.arguments || {};
            if (!id) {
              return {
                content: [{ type: 'text', text: 'Error: Persona ID is required' }],
                isError: true,
              };
            }
            
            const response = await this.apiClient.put(`/personas/${id}`, personaData);
            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(response.data, null, 2),
                },
              ],
            };
          }
          
          case 'delete_persona': {
            const { id } = request.params.arguments || {};
            if (!id) {
              return {
                content: [{ type: 'text', text: 'Error: Persona ID is required' }],
                isError: true,
              };
            }
            
            const response = await this.apiClient.delete(`/personas/${id}`);
            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(response.data, null, 2),
                },
              ],
            };
          }
          
          case 'get_field_config': {
            const { category, field } = request.params.arguments || {};
            const response = await this.apiClient.get('/field-config', {
              params: { category, field }
            });
            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(response.data, null, 2),
                },
              ],
            };
          }
          
          default:
            return {
              content: [{ type: 'text', text: `Unknown tool: ${request.params.name}` }],
              isError: true,
            };
        }
      } catch (error: any) {
        if (axios.isAxiosError(error)) {
          const errorMessage = error.response?.data?.error || 
                               (error.response?.data as any)?.error || 
                               error.message;
          return {
            content: [
              {
                type: 'text',
                text: `API Error: ${errorMessage}`
              },
            ],
            isError: true,
          };
        }
        
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message || String(error)}`
            },
          ],
          isError: true,
        };
      }
    });
  }

  /**
   * Start the MCP server
   */
  async run() {
    console.error(`Persona MCP server connecting to API at: ${API_BASE_URL}`);
    
    // Dynamically import the MCP SDK to avoid TypeScript issues
    const mcp = require('@modelcontextprotocol/sdk');
    const transport = new mcp.StdioServerTransport();
    
    await this.server.connect(transport);
    console.error('Persona MCP server running on stdio');
  }
}

// Create and start the server
const server = new PersonaMcpServer();
server.run().catch(console.error);
