#!/bin/bash
# UNIBOS Git Versioning Script
# Ensures both main and vXXX branches are created and pushed

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${2}${1}${NC}"
}

# Function to extract version from VERSION.json
get_version() {
    if [ -f "src/VERSION.json" ]; then
        grep '"version"' src/VERSION.json | cut -d'"' -f4
    elif [ -f "../src/VERSION.json" ]; then
        grep '"version"' ../src/VERSION.json | cut -d'"' -f4
    else
        echo ""
    fi
}

# Function to create and push version
create_version() {
    local version=$1
    local message=$2
    
    if [ -z "$version" ]; then
        print_message "❌ Error: No version number provided" "$RED"
        return 1
    fi
    
    if [ -z "$message" ]; then
        print_message "❌ Error: No commit message provided" "$RED"
        return 1
    fi
    
    print_message "\n📦 Creating version: $version" "$GREEN"
    print_message "📝 Commit message: $message" "$YELLOW"
    
    # Stage all changes
    print_message "\n1️⃣ Staging changes..." "$YELLOW"
    git add -A
    
    # Commit changes
    print_message "2️⃣ Committing changes..." "$YELLOW"
    git commit -m "$version: $message"
    
    if [ $? -ne 0 ]; then
        print_message "⚠️ No changes to commit or commit failed" "$YELLOW"
        return 1
    fi
    
    # Push to main
    print_message "3️⃣ Pushing to main branch..." "$YELLOW"
    git push origin main
    
    if [ $? -ne 0 ]; then
        print_message "❌ Failed to push to main" "$RED"
        return 1
    fi
    
    # Create or update version branch
    print_message "4️⃣ Creating/updating $version branch..." "$YELLOW"
    
    # Check if branch exists locally
    if git show-ref --verify --quiet refs/heads/$version; then
        print_message "   Branch $version exists locally, updating..." "$YELLOW"
        git checkout $version
        git merge main --no-edit
    else
        print_message "   Creating new branch $version..." "$YELLOW"
        git checkout -b $version
    fi
    
    # Push version branch
    print_message "5️⃣ Pushing $version branch to remote..." "$YELLOW"
    git push origin $version
    
    if [ $? -ne 0 ]; then
        print_message "❌ Failed to push $version branch" "$RED"
        git checkout main
        return 1
    fi
    
    # Return to main
    print_message "6️⃣ Returning to main branch..." "$YELLOW"
    git checkout main
    
    print_message "\n✅ Version $version successfully created and pushed!" "$GREEN"
    print_message "   - main branch: updated ✓" "$GREEN"
    print_message "   - $version branch: created/updated ✓" "$GREEN"
    
    return 0
}

# Main execution
main() {
    print_message "🚀 UNIBOS Git Versioning Tool" "$GREEN"
    print_message "================================\n" "$GREEN"
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_message "❌ Error: Not in a git repository" "$RED"
        exit 1
    fi
    
    # If arguments provided, use them
    if [ $# -eq 2 ]; then
        create_version "$1" "$2"
    else
        # Try to get version from VERSION.json
        version=$(get_version)
        
        if [ -z "$version" ]; then
            print_message "❌ Error: Could not find version in VERSION.json" "$RED"
            print_message "Usage: $0 <version> <commit message>" "$YELLOW"
            print_message "Example: $0 v395 \"Fixed authentication bug\"" "$YELLOW"
            exit 1
        fi
        
        # Get commit message
        if [ $# -eq 1 ]; then
            message="$1"
        else
            print_message "📝 Enter commit message for $version:" "$YELLOW"
            read -r message
        fi
        
        create_version "$version" "$message"
    fi
}

# Run main function
main "$@"