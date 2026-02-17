#!/bin/bash
# Script to update the Desktop shortcut for Fortify

DESKTOP_APP="/Users/andrickjohn/Desktop/Fortify.app"
NEW_APP_SOURCE="/Users/andrickjohn/Projects/Test/.tmp/Fortify.app"

echo "Updating Fortify Desktop shortcut..."

# 1. Remove the old application bundle on Desktop
if [ -d "$DESKTOP_APP" ]; then
    echo "Removing old shortcut..."
    rm -rf "$DESKTOP_APP"
else
    echo "No existing shortcut found on Desktop."
fi

# 2. Move the newly created app bundle to Desktop
if [ -d "$NEW_APP_SOURCE" ]; then
    echo " installing new shortcut..."
    mv "$NEW_APP_SOURCE" "$DESKTOP_APP"
    echo "✅ Success: Fortify shortcut updated on Desktop!"
else
    echo "❌ Error: New app source not found at $NEW_APP_SOURCE"
    exit 1
fi
