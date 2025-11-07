#!/bin/bash
# Database Backup Verification Script
# Verifies SQL backup integrity and provides restore instructions

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

BACKUP_DIR="archive/database_backups"

echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ UNIBOS Database Backup Verification                 ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}❌ Backup directory not found: $BACKUP_DIR${NC}"
    exit 1
fi

# Count backups
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.sql 2>/dev/null | wc -l | tr -d ' ')

if [ "$BACKUP_COUNT" -eq 0 ]; then
    echo -e "${RED}❌ No backups found in $BACKUP_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found ${BACKUP_COUNT} database backup(s)${NC}"
echo ""

echo -e "${CYAN}📋 Backup List:${NC}"
echo ""

# List backups with details
ls -lh "$BACKUP_DIR"/*.sql | while read -r line; do
    FILENAME=$(echo "$line" | awk '{print $9}')
    SIZE=$(echo "$line" | awk '{print $5}')
    DATE=$(echo "$line" | awk '{print $6, $7, $8}')
    BASENAME=$(basename "$FILENAME")

    # Extract version from filename
    VERSION=$(echo "$BASENAME" | grep -o 'v[0-9]*' | head -1)

    # Verify file is readable and has content
    if [ -s "$FILENAME" ]; then
        # Quick JSON validation
        if head -1 "$FILENAME" | grep -q '^\['; then
            STATUS="${GREEN}✓ Valid${NC}"
        else
            STATUS="${YELLOW}⚠ Warning: May not be valid JSON${NC}"
        fi
    else
        STATUS="${RED}✗ Empty file${NC}"
    fi

    echo -e "  ${CYAN}${VERSION}${NC} - $BASENAME"
    echo -e "    Size: $SIZE | Date: $DATE | Status: ${STATUS}"
    echo ""
done

# Show most recent backup details
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/*.sql | head -1)

echo -e "${CYAN}📊 Latest Backup Details:${NC}"
echo -e "  File: $(basename "$LATEST_BACKUP")"
echo -e "  Size: $(du -sh "$LATEST_BACKUP" | cut -f1)"
echo -e "  Modified: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$LATEST_BACKUP" 2>/dev/null || stat -c "%y" "$LATEST_BACKUP" 2>/dev/null)"

# Count records in latest backup
RECORD_COUNT=$(grep -c '^\s*{' "$LATEST_BACKUP" 2>/dev/null || echo "0")
echo -e "  Records: ~${RECORD_COUNT}"

echo ""
echo -e "${CYAN}💡 Restore Instructions:${NC}"
echo ""
echo -e "  To restore from a backup:"
echo -e "  ${YELLOW}cd apps/web/backend${NC}"
echo -e "  ${YELLOW}python manage.py loaddata /path/to/backup.sql${NC}"
echo ""
echo -e "  Example (latest backup):"
echo -e "  ${YELLOW}cd apps/web/backend${NC}"
echo -e "  ${YELLOW}DJANGO_SETTINGS_MODULE=unibos_backend.settings.development \\${NC}"
echo -e "  ${YELLOW}  python manage.py loaddata ../../${LATEST_BACKUP}${NC}"
echo ""

echo -e "${GREEN}✅ Verification complete${NC}"
echo ""
