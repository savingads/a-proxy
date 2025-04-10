#!/usr/bin/env python3
"""
Script to fix dashboard route references in all templates

This script searches for 'persona.dashboard' in all template files and
replaces it with 'persona.create_persona', which is the correct route name.
"""
import os
import re
import logging
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('fix_routes')

def find_and_replace_in_file(filepath):
    """Find and replace dashboard route references in a file"""
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if the file contains the dashboard route
    if 'persona.dashboard' not in content:
        return False
    
    # Replace all occurrences
    new_content = content.replace('persona.dashboard', 'persona.create_persona')
    
    # Write the updated content back to the file
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(new_content)
        
    return True

def scan_directory(directory):
    """Scan directory for template files and fix dashboard route references"""
    templates_dir = Path(directory)
    fixed_files = []
    
    # Find all HTML template files
    for filepath in templates_dir.glob('**/*.html'):
        try:
            if find_and_replace_in_file(filepath):
                logger.info(f"Fixed dashboard route reference in {filepath}")
                fixed_files.append(str(filepath))
        except Exception as e:
            logger.error(f"Error processing {filepath}: {str(e)}")
    
    return fixed_files

def main():
    """Main entry point"""
    # Templates directory relative to the current working directory
    templates_dir = os.path.join(os.getcwd(), 'templates')
    
    if not os.path.exists(templates_dir):
        logger.error(f"Templates directory not found: {templates_dir}")
        return 1
    
    # Scan and fix templates
    fixed_files = scan_directory(templates_dir)
    
    if fixed_files:
        logger.info(f"Fixed dashboard route references in {len(fixed_files)} files:")
        for file in fixed_files:
            logger.info(f"  - {file}")
    else:
        logger.info("No files needed fixing")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
