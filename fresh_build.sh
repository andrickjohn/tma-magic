#!/bin/bash
# Fresh build script for TMA Magic Launcher
# Uses native osacompile for maximum stability

APP_NAME="TMA Magic"
APP_PATH="${HOME}/Desktop/${APP_NAME}.app"
PROJECT_DIR="/Users/john/Projects/test/TMA Project"
ICON_SOURCE="/Users/john/.gemini/antigravity/brain/59f5bc32-3ce5-405c-9403-96522e7abbde/tma_magic_icon_1770593107957.png"

echo "🧹 Cleaning up..."
rm -rf "${APP_PATH}"

echo "🔨 Compiling Native Launcher..."
mkdir -p "${APP_PATH}/Contents/MacOS"
mkdir -p "${APP_PATH}/Contents/Resources"

# Compile the C launcher
clang -o "${APP_PATH}/Contents/MacOS/${APP_NAME}" "${PROJECT_DIR}/launcher.c"

# Set executable permissions
chmod +x "${APP_PATH}/Contents/MacOS/${APP_NAME}"

echo "📝 Creating Info.plist..."
PLIST="${APP_PATH}/Contents/Info.plist"

cat <<EOF > "$PLIST"
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
</dict>
</plist>
EOF

# 1. Hide from Dock (runs as background agent) to prevent 'Not Responding'
plutil -insert LSBackgroundOnly -bool true "$PLIST"

echo "🎨 Applying Icon..."
if [ -f "${ICON_SOURCE}" ]; then
    mkdir -p /tmp/tma_icon.iconset
    sips -s format png -z 16 16     "${ICON_SOURCE}" --out /tmp/tma_icon.iconset/icon_16x16.png >/dev/null
    sips -s format png -z 32 32     "${ICON_SOURCE}" --out /tmp/tma_icon.iconset/icon_16x16@2x.png >/dev/null
    sips -s format png -z 32 32     "${ICON_SOURCE}" --out /tmp/tma_icon.iconset/icon_32x32.png >/dev/null
    sips -s format png -z 64 64     "${ICON_SOURCE}" --out /tmp/tma_icon.iconset/icon_32x32@2x.png >/dev/null
    sips -s format png -z 128 128   "${ICON_SOURCE}" --out /tmp/tma_icon.iconset/icon_128x128.png >/dev/null
    sips -s format png -z 256 256   "${ICON_SOURCE}" --out /tmp/tma_icon.iconset/icon_128x128@2x.png >/dev/null
    sips -s format png -z 256 256   "${ICON_SOURCE}" --out /tmp/tma_icon.iconset/icon_256x256.png >/dev/null
    sips -s format png -z 512 512   "${ICON_SOURCE}" --out /tmp/tma_icon.iconset/icon_256x256@2x.png >/dev/null
    sips -s format png -z 512 512   "${ICON_SOURCE}" --out /tmp/tma_icon.iconset/icon_512x512.png >/dev/null
    sips -s format png -z 1024 1024 "${ICON_SOURCE}" --out /tmp/tma_icon.iconset/icon_512x512@2x.png >/dev/null

    iconutil -c icns /tmp/tma_icon.iconset
    # Native apps use AppIcon.icns
    mv /tmp/tma_icon.icns "${APP_PATH}/Contents/Resources/AppIcon.icns"
    rm -rf /tmp/tma_icon.iconset
fi

echo "🔓 Removing Quarantine..."
xattr -d com.apple.quarantine "${APP_PATH}" 2>/dev/null || true

echo "✨ Done! App created at ${APP_PATH}"
