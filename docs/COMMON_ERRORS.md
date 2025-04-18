# Common Errors and Solutions

This document lists common errors that occur during development and their solutions, serving as a quick reference guide for troubleshooting.

## Database Errors

### "Error listing personas: Unknown error"

**Cause**: Usually occurs due to database initialization issues in the Persona Service, connection issues to the API, or permissions problems.

**Solution**:
1. Ensure the Persona Service database is properly initialized:
   ```bash
   cd _src/persona-service
   python init_db.py
   ```
2. Check API connection:
   ```bash
   curl http://localhost:5050/api/v1/personas
   ```
3. Fix data directory permissions:
   ```bash
   chmod -R 755 _src/persona-service/data
   ```

### SQLAlchemy Text Expression Error

**Error**: "Textual SQL expression should be explicitly declared as text"

**Solution**:
Update SQL queries to use SQLAlchemy's `text()` function:
```python
from sqlalchemy import text
# Instead of: db.engine.execute("SELECT * FROM personas")
db.engine.execute(text("SELECT * FROM personas"))
```

## API Connection Issues

### Connection Failures

**Cause**: Persona service not running or network issues.

**Solution**:
1. Check if the service is running:
   ```bash
   ps aux | grep run.py
   ```
2. Restart the service:
   ```bash
   cd _src/persona-service
   python run.py
   ```
3. Check for network issues:
   ```bash
   curl -v http://localhost:5050/api/v1/health
   ```

### Retry Failures

**Cause**: Temporary connection issues that exceed retry attempts.

**Solution**:
The client now includes a retry mechanism with exponential backoff. If issues persist:
1. Increase the timeout value in `persona_config.py`
2. Check service logs for errors
3. Restart both services

## Repository Management Issues

### Changes Not Reflecting in Application

**Cause**: Local package installation issues or Python path problems.

**Solution**:
1. Reinstall the local package:
   ```bash
   pip uninstall -y agent_module persona-service
   pip install -e _src/agent_module
   ```
2. Restart the application completely
3. Check import statements for correctness

### VSCode Showing Uncommitted Changes

**Cause**: VSCode's git extension detects changes in inner repositories.

**Solution**:
1. Check each repository separately:
   ```bash
   cd _src/persona-service
   git status
   cd ../agent_module
   git status
   cd ../..
   git status
   ```
2. Commit changes in each repository as needed
3. Use the sync-repos.sh script to commit changes across all repositories:
   ```bash
   ./sync-repos.sh "Your commit message"
   ```

## Docker Issues

### Container Connection Problems

**Cause**: Network isolation or port conflicts.

**Solution**:
1. Check if containers are running:
   ```bash
   docker-compose ps
   ```
2. Check logs for errors:
   ```bash
   docker-compose logs
   ```
3. Ensure ports are correctly mapped:
   ```bash
   docker-compose port a-proxy 5002
   ```
4. Restart the containers:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Database Persistence Issues

**Cause**: Volume mounting problems or permission issues.

**Solution**:
1. Check volume mounts:
   ```bash
   docker-compose config
   ```
2. Fix permissions:
   ```bash
   chmod -R 755 data
   ```
3. If needed, reset the database:
   ```bash
   rm -f data/personas.db persona-service/data/persona_service.db
   docker-compose down
   docker-compose up -d
   ```

## JavaScript/TypeScript Errors

### MCP Client Example TypeScript Import Error

**Cause**: ES module imports vs CommonJS require conflicts.

**Solution**:
Change from ES module imports to CommonJS require:
```typescript
// Change from:
// import { MCPClient } from '@anthropic-ai/mcp-client';
// To:
const { MCPClient } = require('@anthropic-ai/mcp-client');
```

## Claude API Integration Issues

### 404: Model Not Found

**Cause**: The specified model name doesn't exist or is unavailable.

**Solution**:
Try a different model in `config.py`:
```python
CLAUDE_MODEL = "claude-3-sonnet-20240229"  # or another available model
```

### 401: Authentication Failed

**Cause**: Invalid or expired API key.

**Solution**:
1. Check your API key in the `.env` file
2. Ensure the key is properly formatted and up-to-date
3. Verify the key has necessary permissions
