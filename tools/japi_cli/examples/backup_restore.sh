#!/bin/bash
# Backup and Restore Script
# Save device configuration to file and restore it later

DEVICE_IP="${1:-192.168.64.100}"
BACKUP_FILE="${2:-device_backup_$(date +%Y%m%d_%H%M%S).json}"

if [ "$1" = "restore" ]; then
    RESTORE_FILE="$2"
    if [ ! -f "$RESTORE_FILE" ]; then
        echo "Error: Restore file '$RESTORE_FILE' not found"
        exit 1
    fi
    
    echo "Restoring device configuration from $RESTORE_FILE..."
    echo "WARNING: This will overwrite current device settings!"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Restore cancelled"
        exit 0
    fi
    
    # TODO: Implement restore functionality
    # This would require parsing the JSON and making appropriate set calls
    echo "Restore functionality not yet implemented"
    echo "Use the backup file to manually configure settings"
    exit 1
else
    echo "Backing up device configuration from $DEVICE_IP to $BACKUP_FILE..."
    
    # Get all configuration and save to file
    python ../japi_cli.py -t $DEVICE_IP setup_get_all > "$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo "Backup saved successfully to $BACKUP_FILE"
        echo "File size: $(du -h "$BACKUP_FILE" | cut -f1)"
        echo ""
        echo "To view backup contents:"
        echo "  cat $BACKUP_FILE | python -m json.tool"
        echo ""
        echo "To restore (manual process):"
        echo "  Use the JSON data to manually configure settings with set commands"
    else
        echo "Backup failed!"
        exit 1
    fi
fi