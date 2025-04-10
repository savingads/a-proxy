#!/bin/bash
# Script to clean up backup (.bak) files

# Check if backup directory exists, if not create it
if [ ! -d "./backup_dev_files" ]; then
    echo "Creating backup directory..."
    mkdir -p ./backup_dev_files
fi

echo "Moving .bak files to backup directory..."

# Create a subdirectory for .bak files
mkdir -p ./backup_dev_files/bak_files

# Find all .bak files (excluding node_modules) and move them to the backup directory
find . -name "*.bak" | grep -v node_modules | while read bakfile; do
    # Create directory structure in backup if needed
    dirname=$(dirname "$bakfile")
    if [ "$dirname" != "." ]; then
        mkdir -p "./backup_dev_files/bak_files/$dirname"
    fi
    
    # Move the file to the backup
    mv "$bakfile" "./backup_dev_files/bak_files/$bakfile"
    echo "Moved: $bakfile"
done

echo "Cleanup complete. All .bak files have been moved to ./backup_dev_files/bak_files/"
