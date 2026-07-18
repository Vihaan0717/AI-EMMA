#!/bin/bash
# Backup script for JARVIS MongoDB Data
# Layer 12: Backups & Recovery

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CONTAINER_NAME="jarvis_project_mongodb_1"

echo "Starting JARVIS MongoDB Backup..."
mkdir -p $BACKUP_DIR

# Run mongodump inside the container and output to archive
docker exec $CONTAINER_NAME sh -c 'mongodump --archive' > $BACKUP_DIR/jarvis_db_$TIMESTAMP.archive

if [ $? -eq 0 ]; then
    echo "✅ Backup successful: $BACKUP_DIR/jarvis_db_$TIMESTAMP.archive"
else
    echo "❌ Backup failed!"
fi
