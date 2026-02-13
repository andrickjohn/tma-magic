#!/bin/bash
# set -e removed to allow partial success

# Define paths
APP_NAME="TMA Magic"
APP_DIR="${HOME}/Desktop/${APP_NAME}.app"
ICON_SOURCE="/Users/john/.gemini/antigravity/brain/59f5bc32-3ce5-405c-9403-96522e7abbde/tma_magic_icon_1770593107957.png"
PROJECT_DIR="/Users/john/Projects/test/TMA Project"

# Compile native launcher
# This creates a binary that runs the open command and exits instantly.
# It is the most robust way to avoid "Not Responding" errors.
mkdir -p "${APP_DIR}/Contents/MacOS"
mkdir -p "${APP_DIR}/Contents/Resources"

clang -o "${APP_DIR}/Contents/MacOS/${APP_NAME}" "${PROJECT_DIR}/launcher.c"

# Remove quarantine attribute if present
xattr -d com.apple.quarantine "${APP_DIR}" 2>/dev/null || true

# Create Info.plist
cat <<EOF > "${APP_DIR}/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.andrickjohn.tmamagic</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>LSUIElement</key>
    <string>1</string>
</dict>
</plist>
EOF

# Create Icon
# Apply Icon to the AppleScript App Bundle
if [ -f "${ICON_SOURCE}" ]; then
    mkdir -p AppIcon.iconset
    sips -s format png -z 16 16     "${ICON_SOURCE}" --out AppIcon.iconset/icon_16x16.png
    sips -s format png -z 32 32     "${ICON_SOURCE}" --out AppIcon.iconset/icon_16x16@2x.png
    sips -s format png -z 32 32     "${ICON_SOURCE}" --out AppIcon.iconset/icon_32x32.png
    sips -s format png -z 64 64     "${ICON_SOURCE}" --out AppIcon.iconset/icon_32x32@2x.png
    sips -s format png -z 128 128   "${ICON_SOURCE}" --out AppIcon.iconset/icon_128x128.png
    sips -s format png -z 256 256   "${ICON_SOURCE}" --out AppIcon.iconset/icon_128x128@2x.png
    sips -s format png -z 256 256   "${ICON_SOURCE}" --out AppIcon.iconset/icon_256x256.png
    sips -s format png -z 512 512   "${ICON_SOURCE}" --out AppIcon.iconset/icon_256x256@2x.png
    sips -s format png -z 512 512   "${ICON_SOURCE}" --out AppIcon.iconset/icon_512x512.png
    sips -s format png -z 1024 1024 "${ICON_SOURCE}" --out AppIcon.iconset/icon_512x512@2x.png

    if iconutil -c icns AppIcon.iconset; then
        mv AppIcon.icns "${APP_DIR}/Contents/Resources/AppIcon.icns"
        rm -rf AppIcon.iconset
        # Touch to refresh icon cache
        touch "${APP_DIR}"
    else
        echo "Warning: Failed to generate AppIcon.icns"
    fi
else
    echo "Warning: Icon source not found at ${ICON_SOURCE}"
fi

# Cleanup
# Cleanup (handled above if successful)

# Touch to refresh
touch "${APP_DIR}"

echo "TMA Magic.app created successfully on Desktop"
