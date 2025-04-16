# Synchronization Plan for Local Package Structure

## Current Structure

The A-Proxy project has moved from git submodules to a local package approach:

- The main repository contains the core application code
- The `_src` directory contains local copies of dependencies:
  - `_src/persona-service` - Persona API service
  - `_src/agent_module` - Agent functionality

Each of these directories is its own git repository, but they are installed locally as Python packages using `pip install -e`.

## Why Uncommitted Changes Appear

VSCode's git extension may show uncommitted changes even when `git status` in the terminal shows none. This happens because:

1. VSCode's git extension automatically looks into all directories, including `_src/*`
2. These inner directories are their own git repositories
3. Changes to files in `_src/persona-service` or `_src/agent_module` are detected by VSCode's git extension
4. The main repository is not tracking these directories directly (they're excluded in .gitignore)

## Synchronization Plan

### 1. Directory-Specific Commits

When making changes to files in the project:

- **Main Repository Changes**: Use git commands in the root directory
- **Persona Service Changes**: Use git commands within the `_src/persona-service` directory
- **Agent Module Changes**: Use git commands within the `_src/agent_module` directory

```bash
# Example: Commit changes to persona service
cd _src/persona-service
git add .
git commit -m "Add feature to persona service"
```

### 2. Synchronization Script

Create a script to help manage changes across repositories:

```bash
#!/bin/bash
# sync-repos.sh

# Commit changes to persona-service
echo "Syncing persona-service repository..."
cd _src/persona-service
git add .
git commit -m "$1"
git push origin develop

# Commit changes to agent_module
echo "Syncing agent_module repository..."
cd ../../_src/agent_module
git add .
git commit -m "$1"
git push origin personas

# Commit changes to main repository
echo "Syncing main repository..."
cd ../..
git add .
git commit -m "$1"
git push origin develop

echo "Synchronization complete!"
```

### 3. Version Tracking

- Use `VERSION.txt` in the root directory to track the overall version
- Each component specifies compatible version ranges for dependencies
- When updating components, update version information accordingly

### 4. Development Workflow

1. Make changes to appropriate directories based on the component you're modifying
2. Test changes locally using `start-with-packages.sh`
3. Commit changes to each repository separately, or use the sync script
4. Update documentation if the change affects the integration between components

### 5. Merge and Release Process

When preparing a release:

1. Ensure all inner repository changes are committed and pushed
2. Tag inner repositories with appropriate version numbers
3. Update references in the main repository to point to specific tags
4. Update `VERSION.txt` with the new release version
5. Tag the main repository

## Benefits of This Approach

- **Clear Boundaries**: Each repository has clear responsibilities
- **Independent Versioning**: Components can be versioned independently
- **Simplified Development**: No need to manage complex git submodule operations
- **Transparent Changes**: Changes to inner repositories are visible but separate
- **Flexible Integration**: Components can be used by other projects
