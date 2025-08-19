#!/bin/bash
# UNIBOS Push All Versions Script
# Purpose: Push all version branches and tags to GitHub efficiently
# Created: 2025-08-19

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   UNIBOS Version Push Script           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo

# Function to push a version
push_version() {
    local version=$1
    local branch_exists=$(git show-ref --verify --quiet refs/heads/$version && echo "yes" || echo "no")
    local tag_exists=$(git show-ref --verify --quiet refs/tags/$version && echo "yes" || echo "no")
    
    echo -e "${CYAN}Processing $version...${NC}"
    
    # Push branch if exists
    if [ "$branch_exists" = "yes" ]; then
        # First checkout and merge main
        git checkout "$version" 2>/dev/null
        git merge main --no-edit 2>/dev/null
        
        # Push branch
        if git push -f origin "refs/heads/$version:refs/heads/$version" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} Branch pushed"
        else
            echo -e "  ${RED}✗${NC} Branch push failed"
            return 1
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} Branch not found locally"
    fi
    
    # Push tag if exists
    if [ "$tag_exists" = "yes" ]; then
        if git push -f origin "refs/tags/$version:refs/tags/$version" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} Tag pushed"
        else
            echo -e "  ${RED}✗${NC} Tag push failed"
        fi
    else
        echo -e "  ${YELLOW}⚠${NC} Tag not found locally"
    fi
    
    return 0
}

# Save current branch
ORIGINAL_BRANCH=$(git branch --show-current)

# Statistics
TOTAL=0
SUCCESS=0
FAILED=0

# Get all version branches and tags
echo -e "${YELLOW}🔍 Detecting versions...${NC}"
echo

# Collect all version names (from both branches and tags)
ALL_VERSIONS=$(
    {
        git branch --list 'v[0-9]*' | sed 's/^[* ]*//'
        git tag --list 'v[0-9]*'
    } | sort -V | uniq
)

# Count total versions
TOTAL=$(echo "$ALL_VERSIONS" | wc -l | tr -d ' ')

if [ "$TOTAL" -eq 0 ]; then
    echo -e "${RED}No version branches or tags found!${NC}"
    exit 1
fi

echo -e "${BLUE}Found $TOTAL versions to process${NC}"
echo

# Optional: Ask for confirmation
echo -n "Push all versions to GitHub? (yes/no): "
read CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}Cancelled.${NC}"
    exit 0
fi

echo
echo -e "${YELLOW}🚀 Starting push operation...${NC}"
echo

# Progress counter
CURRENT=0

# Process each version
for VERSION in $ALL_VERSIONS; do
    CURRENT=$((CURRENT + 1))
    echo -e "${BLUE}[$CURRENT/$TOTAL]${NC} Version: $VERSION"
    
    if push_version "$VERSION"; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
    fi
    
    echo
done

# Return to original branch
echo -e "${YELLOW}Returning to $ORIGINAL_BRANCH...${NC}"
git checkout "$ORIGINAL_BRANCH" 2>/dev/null

echo
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ PUSH OPERATION COMPLETE${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo
echo "📊 Summary:"
echo -e "   Total versions: ${CYAN}$TOTAL${NC}"
echo -e "   ${GREEN}✓ Successful: $SUCCESS${NC}"
echo -e "   ${RED}✗ Failed: $FAILED${NC}"

# Verify remote status
echo
echo -e "${YELLOW}📡 Verifying remote status...${NC}"

# Count remote branches and tags
REMOTE_BRANCHES=$(git ls-remote --heads origin | grep -c "refs/heads/v[0-9]" || echo "0")
REMOTE_TAGS=$(git ls-remote --tags origin | grep -c "refs/tags/v[0-9]" || echo "0")

echo -e "   Remote branches: ${CYAN}$REMOTE_BRANCHES${NC}"
echo -e "   Remote tags: ${CYAN}$REMOTE_TAGS${NC}"

echo
echo -e "${GREEN}✅ All operations completed!${NC}"

# Optional: Show latest versions
echo
echo -e "${BLUE}Latest 5 versions on GitHub:${NC}"
git ls-remote --heads origin | grep "refs/heads/v[0-9]" | tail -5 | while read hash ref; do
    version=$(echo $ref | sed 's|refs/heads/||')
    short_hash=$(echo $hash | cut -c1-7)
    echo -e "   $version: $short_hash"
done
