#!/bin/bash
# Script to clean up development and backup files

# Create backup directory
echo "Creating backup directory..."
mkdir -p ./backup_dev_files

# Files with _fixed or _updated suffixes
echo "Moving *_fixed* and *_updated* files to backup..."
find . -name "*_fixed*" -o -name "*_updated*" | grep -v __pycache__ | xargs -I{} mv {} ./backup_dev_files/

# Migration and implementation scripts
echo "Moving migration and implementation scripts to backup..."
MIGRATION_FILES="implement_dynamic_personas.py implement_ui_changes.py fix_implementation.py fix_dashboard_references.py standalone_migration.py direct_migration.py manual_migrate.py migrate_to_api.py persona-service/migrate_schema_fixed.py persona-service/migrate_schema.py"
for file in $MIGRATION_FILES; do
  if [ -f "$file" ]; then
    mv "$file" ./backup_dev_files/
  fi
done

# Testing scripts
echo "Moving test scripts to backup..."
TEST_FILES="test_api.py test_client.py create_persona.py"
for file in $TEST_FILES; do
  if [ -f "$file" ]; then
    mv "$file" ./backup_dev_files/
  fi
done

# Restore important files that we actually need
echo "Restoring essential implementation files..."
KEEP_FILES=(
  "app_with_db.py"
  "utils/persona_client_db.py" 
  "routes/persona_api_db.py" 
  "start_a_proxy_all.py"
)

for file in "${KEEP_FILES[@]}"; do
  if [ -f "./backup_dev_files/$file" ]; then
    cp "./backup_dev_files/$file" "./$file"
  fi
done

echo "Cleanup complete. All development files have been moved to ./backup_dev_files/"
echo "You can review these files and delete the backup directory when you're sure everything is working."
