# Claude API Integration Guide

This document explains how to integrate Claude AI into the a-proxy agent system.

## Configuration

The Claude API integration requires a valid Anthropic API key. To set up the integration:

1. Update the `config.py` file with your Anthropic API key or set it as an environment variable
2. Configure the model and parameters according to your Anthropic API access level

## Available Configuration Options

```python
# Claude API configuration in config.py
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', 'your-api-key-here')
CLAUDE_MODEL = 'claude-3-opus-20240229'  # Change to the model you have access to
CLAUDE_MAX_TOKENS = 4096  # Response length limit

# Agent module configuration
AGENT_USE_CLAUDE = True  # Set to False to disable Claude integration
AGENT_REQUIRE_AUTH = False  # Whether authentication is required
```

## Available Claude Models

Depending on your API access level, you may have access to different models:

- `claude-3-opus-20240229` - Latest and most capable Claude model
- `claude-3-sonnet-20240229` - Balanced performance and cost
- `claude-3-haiku-20240307` - Fastest and most economical
- `claude-2.1` - Legacy model
- `claude-2.0` - Legacy model
- `claude-instant-1.2` - Legacy model

**Note:** Your API key must have access to the specified model.

## Testing the Integration

Once configured, the agent module will automatically use Claude when:

1. The `AGENT_USE_CLAUDE` setting is `True`
2. The specified Claude model is accessible with your API key
3. The agent module's adapter factory is correctly configured

To verify the integration is working:

1. Start the application
2. Navigate to the direct chat interface
3. Send a test message
4. Check the application logs for any Claude API errors

## Troubleshooting

If you encounter issues with the Claude integration:

1. **404 Model Not Found Error**: Your API key doesn't have access to the specified model. Try a different model name.
2. **401 Unauthorized Error**: The API key is invalid or expired.
3. **API Response Issues**: Check the anthropic-version header in the adapter code matches the API version for your key.

## Advanced Configuration

For advanced users, the Claude adapter can be customized by modifying the following files:

- `agent_module/adapters/a_proxy_claude.py` - Main Claude adapter implementation
- `config.py` - Configuration settings

## Example Usage

```python
# Example of manually using the Claude adapter
from agent_module.adapters.a_proxy_claude import AProxyClaudeAdapter
from agent_module.services.config_service import ConfigService

# Create the adapter
adapter = AProxyClaudeAdapter(config_service=ConfigService())

# Send a message
response = adapter.send_message("Hello, Claude!")
print(response['content'])
