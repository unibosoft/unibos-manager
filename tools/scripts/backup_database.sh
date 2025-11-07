#!/bin/bash
# Database Backup Script for UNIBOS
# Creates timestamped SQL dumps and maintains last 3 versions
# These backups are SEPARATE from version archives

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKUP_DIR="$PROJECT_ROOT/archive/database_backups"
DJANGO_DIR="$PROJECT_ROOT/apps/web/backend"
SETTINGS_MODULE="unibos_backend.settings.development"
KEEP_BACKUPS=3  # Keep last 3 backups

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ UNIBOS Database Backup System                       ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# Get version info
VERSION=""
if [ -f "$DJANGO_DIR/VERSION.json" ]; then
    VERSION=$(grep '"version"' "$DJANGO_DIR/VERSION.json" | head -1 | sed 's/.*"v/v/' | sed 's/".*//')
fi

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup filename with version
if [ -n "$VERSION" ]; then
    BACKUP_FILE="${BACKUP_DIR}/unibos_${VERSION}_${TIMESTAMP}.sql"
else
    BACKUP_FILE="${BACKUP_DIR}/unibos_backup_${TIMESTAMP}.sql"
fi

echo -e "${CYAN}📦 Creating database backup...${NC}"
echo -e "${YELLOW}   File: ${BACKUP_FILE}${NC}"
echo ""

# Check if we're in development or production
if [ -d "$DJANGO_DIR/venv" ]; then
    PYTHON="$DJANGO_DIR/venv/bin/python"
else
    PYTHON="python3"
fi

# Create the backup using Django's dumpdata
cd "$DJANGO_DIR"
DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE" $PYTHON manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --indent 2 \
    --exclude contenttypes \
    --exclude auth.permission \
    --exclude sessions.session \
    > "$BACKUP_FILE"

# Check if backup was successful
if [ -f "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✅ Backup created successfully!${NC}"
    echo -e "${GREEN}   Size: ${BACKUP_SIZE}${NC}"
    echo -e "${GREEN}   Location: ${BACKUP_FILE}${NC}"
    echo ""
else
    echo -e "${RED}❌ Backup failed!${NC}"
    exit 1
fi

# Cleanup old backups (keep last 3)
echo -e "${CYAN}🗑️  Cleaning up old backups (keeping last ${KEEP_BACKUPS})...${NC}"

# Count current backups
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.sql 2>/dev/null | wc -l | tr -d ' ')

if [ "$BACKUP_COUNT" -gt "$KEEP_BACKUPS" ]; then
    # Delete oldest backups
    DELETE_COUNT=$((BACKUP_COUNT - KEEP_BACKUPS))
    echo -e "${YELLOW}   Found ${BACKUP_COUNT} backups, deleting ${DELETE_COUNT} oldest...${NC}"

    ls -1t "$BACKUP_DIR"/*.sql | tail -n "$DELETE_COUNT" | while read old_backup; do
        echo -e "${YELLOW}   Deleting: $(basename "$old_backup")${NC}"
        rm -f "$old_backup"
    done

    echo -e "${GREEN}✅ Cleanup complete${NC}"
else
    echo -e "${GREEN}   Currently ${BACKUP_COUNT} backups (within limit)${NC}"
fi

echo ""
echo -e "${CYAN}📊 Current backups:${NC}"
ls -lh "$BACKUP_DIR"/*.sql 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'

echo ""
echo -e "${GREEN}✅ Database backup complete!${NC}"
echo ""
