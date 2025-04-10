#!/usr/bin/env python3
"""
Script to implement the dynamic persona field configuration system

This script:
1. Backs up existing files
2. Copies the updated models, services, and routes to their proper locations
3. Updates the app to use the dynamic templates
4. Runs the database migration if requested
"""
import os
import sys
import shutil
import argparse
import logging
import subprocess
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('implementation')

def backup_file(file_path):
    """Backup a file by appending timestamp to filename"""
    if not os.path.exists(file_path):
        logger.warning(f"File does not exist, cannot backup: {file_path}")
        return
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.{timestamp}.bak"
    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backed up {file_path} to {backup_path}")
    except Exception as e:
        logger.error(f"Failed to backup {file_path}: {str(e)}")
        
def copy_file(src, dest):
    """Copy a file and create parent directories if needed"""
    try:
        # Ensure source file exists
        if not os.path.exists(src):
            logger.error(f"Source file does not exist: {src}")
            return False
            
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        
        shutil.copy2(src, dest)
        logger.info(f"Copied {src} to {dest}")
        return True
    except Exception as e:
        logger.error(f"Failed to copy {src} to {dest}: {str(e)}")
        return False

def update_app_for_dynamic_templates():
    """Update app.py to use dynamic templates and updated persona API routes"""
    app_path = "app.py"
    backup_file(app_path)
    
    try:
        with open(app_path, 'r') as f:
            content = f.read()
            
        # Replace persona blueprint import
        if "from routes.persona_api import persona_bp" in content:
            content = content.replace(
                "from routes.persona_api import persona_bp",
                "from routes.persona_api_updated import persona_bp"
            )
        elif "from routes.persona import persona_bp" in content:
            content = content.replace(
                "from routes.persona import persona_bp",
                "from routes.persona_api_updated import persona_bp"
            )
        else:
            logger.warning("Could not find persona blueprint import in app.py")
        
        # Write updated content
        with open(app_path, 'w') as f:
            f.write(content)
            
        logger.info("Updated app.py to use dynamic persona templates")
        return True
    except Exception as e:
        logger.error(f"Failed to update app.py: {str(e)}")
        return False

def update_import_in_persona_api():
    """Update import in persona_api_updated.py to include session"""
    api_path = "routes/persona_api_updated.py"
    
    try:
        with open(api_path, 'r') as f:
            content = f.read()
            
        # Add session import if needed
        if "from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, abort" in content:
            content = content.replace(
                "from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, abort",
                "from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, abort, session"
            )
        
        # Write updated content
        with open(api_path, 'w') as f:
            f.write(content)
            
        logger.info("Updated imports in persona_api_updated.py")
        return True
    except Exception as e:
        logger.error(f"Failed to update persona_api_updated.py: {str(e)}")
        return False
    
def run_migration(db_uri=None, dry_run=True):
    """Run the database migration script"""
    try:
        # Use the fixed migration script
        cmd = ["python", "persona-service/migrate_schema_fixed.py"]
        
        if dry_run:
            cmd.append("--dry-run")
            
        if db_uri:
            cmd.extend(["--db-uri", db_uri])
            
        logger.info(f"Running migration: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        logger.info(f"Migration stdout: {result.stdout}")
        
        if result.stderr:
            logger.warning(f"Migration stderr: {result.stderr}")
            
        if result.returncode != 0:
            logger.error(f"Migration failed with return code {result.returncode}")
            return False
            
        logger.info("Migration completed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to run migration: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Implement dynamic persona fields')
    parser.add_argument('--migrate', action='store_true', help='Run database migration after implementation')
    parser.add_argument('--db-uri', help='Database URI for migration')
    parser.add_argument('--no-backup', action='store_true', help='Skip file backups')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no actual migration)')
    args = parser.parse_args()
    
    # List of files to copy
    files_to_copy = [
        # Source file is the current file, destination is the target
        ("persona_field_config.py", "persona_field_config.py"),
        ("persona-service/app/models_updated.py", "persona-service/app/models.py"),
        ("persona-service/app/services_updated.py", "persona-service/app/services.py"),
        ("persona-service/app/routes_updated.py", "persona-service/app/routes.py"),
        ("templates/persona_view_dynamic.html", "templates/persona_view.html"),
        ("templates/persona_edit_dynamic.html", "templates/persona_edit.html"),
        ("routes/persona_api_updated.py", "routes/persona_api.py"),
        ("persona-service/migrate_schema_fixed.py", "persona-service/migrate_schema.py")
    ]
    
    # Backup and copy files
    for src, dest in files_to_copy:
        if not args.no_backup:
            backup_file(dest)
        copy_file(src, dest)
    
    # Update the app
    update_app_for_dynamic_templates()
    update_import_in_persona_api()
    
    # Run migration if requested
    if args.migrate:
        run_migration(args.db_uri, args.dry_run)
    
    logger.info("Dynamic persona field implementation completed")
    
    if not args.migrate:
        logger.info("To run the database migration, use: python persona-service/migrate_schema.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
