#!/bin/bash
# Migration Check Script for UNIBOS
# Ensures all migrations are applied before deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DJANGO_DIR="apps/web/backend"
SETTINGS_MODULE="unibos_backend.settings.development"

echo -e "${CYAN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ UNIBOS Migration Check System                       ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're on local or remote
if [ -d "$DJANGO_DIR/venv" ]; then
    PYTHON="$DJANGO_DIR/venv/bin/python"
else
    PYTHON="python3"
fi

cd "$DJANGO_DIR"

echo -e "${CYAN}📋 Checking for unapplied migrations...${NC}"
UNAPPLIED=$(DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE" $PYTHON manage.py showmigrations --plan | grep "\[ \]" || true)

if [ -n "$UNAPPLIED" ]; then
    echo -e "${YELLOW}⚠️  Found unapplied migrations:${NC}"
    echo "$UNAPPLIED"
    echo ""

    read -p "Apply migrations now? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${CYAN}🔄 Applying migrations...${NC}"
        DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE" $PYTHON manage.py migrate
        echo -e "${GREEN}✅ Migrations applied successfully${NC}"
    else
        echo -e "${RED}❌ Deployment aborted - migrations must be applied${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ All migrations are up to date${NC}"
fi

echo ""
echo -e "${CYAN}📊 Checking for model changes not in migrations...${NC}"
CHANGES=$(DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE" $PYTHON manage.py makemigrations --dry-run 2>&1 | grep "No changes detected" || true)

if [ -z "$CHANGES" ]; then
    echo -e "${YELLOW}⚠️  Found model changes not reflected in migrations${NC}"
    echo -e "${YELLOW}   Run 'python manage.py makemigrations' to create migrations${NC}"
    echo ""

    read -p "Create migrations now? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${CYAN}🔄 Creating migrations...${NC}"
        DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE" $PYTHON manage.py makemigrations
        echo -e "${GREEN}✅ Migrations created${NC}"

        echo -e "${CYAN}🔄 Applying new migrations...${NC}"
        DJANGO_SETTINGS_MODULE="$SETTINGS_MODULE" $PYTHON manage.py migrate
        echo -e "${GREEN}✅ Migrations applied${NC}"
    else
        echo -e "${RED}❌ Deployment aborted - model changes must be migrated${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ No pending model changes${NC}"
fi

echo ""
echo -e "${GREEN}✅ Migration check complete!${NC}"
echo ""
