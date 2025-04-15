./# Claude Agent Integration

This document explains how to use the standalone Claude agent integration in a-proxy.

## Overview

We've created a direct Claude interface that lets you interact with Claude without needing to create a journey or persona. This provides a streamlined way to test and use Claude's capabilities.

## Features

- Direct chat interface with Claude
- Support for different Claude models (Opus, Sonnet, Haiku)
- Custom system prompt configuration
- Stateless conversations (each session starts fresh)
- Simple, clean interface dedicated to Claude interaction

## Accessing Claude

### Web Interface

The Claude agent interface is available at:

```
http://localhost:5002/agent
```

This provides a full interface with:
- Model selection dropdown
- System prompt configuration
- Chat history within the current session
- Reset button to start fresh

### API Endpoints

For programmatic access:

- **POST** `/agent/message` - Send a message to Claude
  - Parameters:
    - `message` (required): The message to send
    - `conversation_id` (optional): ID for the conversation
    - `model` (optional): The Claude model to use
    - `system_prompt` (optional): Custom system prompt

## Testing

A test script is provided to verify the Claude integration:

```bash
python test_standalone_agent.py --message "Hello, Claude!" --model "claude-3-opus-20240229"
```

Additional options:
```bash
python test_standalone_agent.py --system-prompt "You are a helpful assistant specialized in science" --message "Tell me about black holes"
```

## Implementation Notes

- Uses the official Anthropic Python SDK
- Features an automatic model fallback system if the primary model is unavailable
- Completely independent of the journey/waypoint system
- Built with memory-free design (no persistence between sessions)
