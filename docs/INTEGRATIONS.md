# Integrations & Migration Guide

This document consolidates all integration and migration notes for A-Proxy, including agent module, Claude, and TypeScript/MCP integrations.

---

## 1. Agent Module Integration
A-Proxy integrates the `agent_module` (as a submodule) to provide AI assistant capabilities within journey workflows.

- **Submodule:** `agent_module` is included as a submodule for separation and maintainability.
- **Database:** Waypoints table includes `type` (regular/agent) and `agent_data` (JSON conversation data).
- **Service Layer:** `utils/agent.py` wraps agent module functionality.
- **UI:** `agent_waypoint.html` and `agent_waypoint_summary.html` for chat and summary views; "Ask Agent" buttons in journey pages.
- **Routes:** `routes/agent.py` handles agent chat, message processing, and saving conversations as waypoints.

**Usage:**
- Access the agent from journey views via "Ask Agent".
- Save agent conversations as waypoints in the journey timeline.

**Future:**
- Deeper journey context, customizable agent personas, enhanced visualization, export options.

---

## 2. Claude Agent Integration
A-Proxy supports direct Claude agent interaction, independent of journeys/personas.

- **Environment:** Store your Claude API key in `.env` as `ANTHROPIC_API_KEY`.
- **Web Interface:** Available at `http://localhost:5002/agent` with model selection, system prompt, and chat history.
- **API:**
  - `POST /agent/message` with `message`, `model`, `system_prompt`.
- **Testing:** Use `test_standalone_agent.py` to verify integration.
- **Notes:** Uses Anthropic SDK, supports model fallback, stateless by design.

---

## 3. Claude API Integration
- **Configuration:**
  - Set `ANTHROPIC_API_KEY` in `config.py` or as an environment variable.
  - Choose model (`claude-3-opus-20240229`, `claude-3-sonnet-20240229`, etc.).
  - Set `AGENT_USE_CLAUDE = True` to enable.
- **Adapter:** `AProxyClaudeAdapter` in `agent_module/adapters/a_proxy_claude.py` implements LLMServiceAdapter.
- **Fallback:** Tries multiple models if the preferred one is unavailable.
- **Troubleshooting:**
  - 404: Model not found (try a different model)
  - 401: Invalid/expired API key
  - Check API version headers and logs for errors.
- **Advanced:** Customize adapter in `a_proxy_claude.py` and config in `config.py`.

---

## 4. Implementation Summary
- **Adapter:** Handles conversation context, persona info, and model fallback.
- **Configuration:** All settings in `config.py`.
- **Usage:** Agent will use Claude automatically if enabled and configured.
- **Testing:** Start the app, use the chat interface, and check logs for fallback/model selection.
- **Future:** API key validation, caching, advanced persona/context, admin UI for Claude settings.

---

## 5. TypeScript & MCP Integration
- **TypeScript Fix:** Use CommonJS `require()` in `mcp-client-example.ts` for compatibility.
- **Development Scripts:**
  - `setup-dev-environment.sh` sets up persona-service and MCP client.
  - `run-dev-without-docker-fixed.sh` starts Persona Service API and runs MCP client example.
- **Directory Structure:**
  - `persona-service/` for the main service
  - `persona-mcp-server/examples/` for MCP client example
- **Notes:** Scripts handle submodule normalization; direct file usage is preferred for most dev tasks.

---

## 6. References & Further Reading
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system overview.
- See [config.py](config.py) for all integration settings.
- See `agent_module/adapters/a_proxy_claude.py` for Claude adapter code.
- See `persona-mcp-server/examples/` for MCP client examples.
