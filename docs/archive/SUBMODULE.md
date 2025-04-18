# Working with the Persona Service Submodule

This project now uses a Git submodule to integrate the Persona Service. This document explains how to work with this setup.

## Overview

The Persona Service has been moved to a standalone repository and is integrated as a Git submodule in this project. This approach provides several benefits:

- Clear separation of concerns between the main application and the persona service
- Ability to version and manage the persona service independently
- Easy updates when the persona service is enhanced
- Simplified deployment options

## Getting Started

### Initial Clone

When cloning this repository for the first time, you need to include the submodule:

```bash
# Clone with submodules included
git clone --recurse-submodules [repository-url]

# OR, if you've already cloned without submodules:
git submodule update --init --recursive
```

### Starting the Application

A new script has been provided to start the application with the submodule:

```bash
./start-with-submodule.sh
```

This will spin up the entire stack using Docker Compose with the persona service from the submodule.

## Development Workflow

### Updating the Submodule

To update the persona service to the latest version:

```bash
# Navigate to the submodule directory
cd persona-service-new

# Get the latest changes
git pull origin main

# Go back to the main project
cd ..

# Commit the submodule update
git add persona-service-new
git commit -m "Update persona service submodule"
```

### Making Changes to the Persona Service

If you need to make changes to the persona service code:

1. Navigate to the submodule directory: `cd persona-service-new`
2. Create a branch: `git checkout -b feature/my-new-feature`
3. Make your changes
4. Commit and push the changes to the persona service repository
5. Navigate back to the main project: `cd ..`
6. Update the submodule reference: `git add persona-service-new`
7. Commit the update: `git commit -m "Update persona service submodule to include feature/my-new-feature"`

### Configuration

The application is configured to use the persona service from the submodule. The following environment variables control this integration:

- `PERSONA_API_URL`: Set to the URL of the persona service (default: http://localhost:5050)
- `PERSONA_API_VERSION`: API version to use (default: v1)
- `PERSONA_API_TIMEOUT`: Timeout for API requests in seconds (default: 10)

## Deployment Considerations

When deploying with the submodule, ensure:

1. Your CI/CD pipeline includes submodule initialization: `git submodule update --init --recursive`
2. Docker Compose configuration (`docker-compose-submodule.yml`) is used for deployment
3. Your build process properly builds both the main application and the submodule

## Troubleshooting

### Submodule Not Properly Initialized

If you see errors about missing files in the persona service, ensure the submodule is properly initialized:

```bash
git submodule update --init --recursive
```

### Changes Not Applied

If your changes to the persona service aren't being reflected:

1. Verify you've committed and pushed changes in the submodule repository
2. Update the submodule reference in the main project with `git add persona-service-new`
3. Commit the update
