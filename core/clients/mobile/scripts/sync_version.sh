#!/bin/bash
# sync version from core VERSION.json to mobile

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MOBILE_DIR="$(dirname "$SCRIPT_DIR")"
UNIBOS_ROOT="$(dirname "$(dirname "$(dirname "$MOBILE_DIR")")")"
VERSION_FILE="$UNIBOS_ROOT/VERSION.json"
PUBSPEC_FILE="$MOBILE_DIR/pubspec.yaml"
ASSETS_VERSION="$MOBILE_DIR/assets/VERSION.json"

# check if VERSION.json exists
if [ ! -f "$VERSION_FILE" ]; then
    echo "error: VERSION.json not found at $VERSION_FILE"
    exit 1
fi

# read version info
MAJOR=$(python3 -c "import json; print(json.load(open('$VERSION_FILE'))['version']['major'])")
MINOR=$(python3 -c "import json; print(json.load(open('$VERSION_FILE'))['version']['minor'])")
PATCH=$(python3 -c "import json; print(json.load(open('$VERSION_FILE'))['version']['patch'])")
BUILD=$(python3 -c "import json; print(json.load(open('$VERSION_FILE'))['version']['build'])")

VERSION="$MAJOR.$MINOR.$PATCH"
FULL_VERSION="$VERSION+$BUILD"

echo "syncing version: $FULL_VERSION"

# update pubspec.yaml
if [ -f "$PUBSPEC_FILE" ]; then
    sed -i '' "s/^version: .*/version: $FULL_VERSION/" "$PUBSPEC_FILE"
    echo "updated pubspec.yaml"
fi

# copy VERSION.json to assets
cp "$VERSION_FILE" "$ASSETS_VERSION"
echo "copied VERSION.json to assets"

echo "version sync complete: $FULL_VERSION"
