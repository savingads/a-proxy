# Docker Security Guide

## API Key Security ✅

The Docker container is now **properly secured** and does NOT contain any API keys in the image.

### How API Keys Are Handled

1. **✅ Secure**: The `.env` file with your real API key is excluded from the Docker build via `.dockerignore`
2. **✅ Default**: The container uses `.env.docker` with empty `ANTHROPIC_API_KEY=`
3. **✅ Runtime**: API keys should be provided at runtime via environment variables

### Running with API Key

#### Option 1: Environment Variable
```bash
docker run -e ANTHROPIC_API_KEY=your-api-key-here a-proxy
```

#### Option 2: Docker Compose with Environment
```yaml
services:
  a-proxy:
    environment:
      ANTHROPIC_API_KEY: your-api-key-here
```

#### Option 3: External .env File
```bash
# Create a separate .env file outside the build context
echo "ANTHROPIC_API_KEY=your-api-key-here" > /secure/path/.env

# Mount it at runtime
docker run --env-file /secure/path/.env a-proxy
```

### Verification

You can verify the container doesn't contain your API key:

```bash
# Check what's in the container's .env file
docker exec container-name cat /app/.env

# Should show: ANTHROPIC_API_KEY=
```

### What Works Without API Key

- ✅ User authentication and login
- ✅ Persona management and browsing  
- ✅ Dashboard and navigation
- ✅ Database operations
- ❌ AI chat functionality (requires API key)

The application will gracefully handle missing API keys and show appropriate error messages for AI features.