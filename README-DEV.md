# A-Proxy Development Guide

## Starting the Application in Development Mode

The recommended way to start A-Proxy in development mode is using the `start-with-packages.sh` script:

```bash
./start-with-packages.sh
```

This script will:
1. Set up the necessary environment (virtual environment, Python packages, etc.)
2. Initialize the persona-service database if needed
3. Create sample personas if none exist
4. Start both the persona-service API and A-Proxy web application
5. Clean up processes when you exit (Ctrl+C)

## Development Approach: Local Packages

We use a local package approach for managing dependencies like `agent_module` and `persona-service`. This approach:
- Makes development easier with immediate code changes
- Avoids git submodule synchronization issues
- Provides better separation between repositories

The source code for these packages is stored in the `_src` directory:
- `_src/agent_module/`: Agent module code (personas branch)
- `_src/persona-service/`: Persona service code (develop branch)

## Utility Scripts

Several utility scripts are available in the `scripts/utilities/` directory:

### Package Management
- `switch-to-local-packages.sh`: Converts from submodules to local packages (run once on setup)
- `fix-persona-service-dependencies.sh`: Fixes persona-service dependencies if needed

### Data Tools
- `fix-create-personas.sh`: Forces creation of sample personas if they're missing

## Development Notes

1. **Making Changes**:
   - Edit code directly in the `_src/` directories
   - Changes take effect immediately without needing to reinstall packages

2. **Adding New Personas**:
   - Use the persona UI at http://localhost:5002/personas
   - Alternatively, run `scripts/utilities/fix-create-personas.sh` to recreate sample personas

3. **Database Location**:
   - Persona Service database: `_src/persona-service/data/persona_service.db`
   - A-Proxy database (if used): `data/aproxy.db`

4. **Logs & Debugging**:
   - The `start-with-packages.sh` script displays logs from both services in the terminal
   - Debug messages include Werkzeug outputs, request information, and application logs
