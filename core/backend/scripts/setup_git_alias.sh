#!/bin/bash
# Setup git alias for UNIBOS versioning

echo "Setting up UNIBOS git versioning alias..."

# Add custom git command
git config --global alias.unibos-version '!python3 $(git rev-parse --show-toplevel)/backend/scripts/git_version.py'

echo "✅ Git alias created!"
echo ""
echo "Usage examples:"
echo "  git unibos-version                    # Auto-detect version from VERSION.json"
echo "  git unibos-version v395 \"Bug fix\"     # Specify version and message"
echo "  git unibos-version --auto              # Auto-confirm without prompting"
echo "  git unibos-version --update-json       # Also update VERSION.json"
echo ""
echo "You can now use: git unibos-version"