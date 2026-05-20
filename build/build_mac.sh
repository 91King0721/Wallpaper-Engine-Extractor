#!/bin/bash
# Build macOS .app wrapper (requires Python 3 installed on user's machine)
# Usage: bash build/build_mac.sh

cd "$(dirname "$0")/.."
NAME="WallpaperEngineExtractor"
APP_PATH="dist/${NAME}.app"
ZIP_PATH="dist/${NAME}_macOS.zip"

echo "=== Building macOS .app (script wrapper) ==="
rm -rf "${APP_PATH}" "${ZIP_PATH}"

mkdir -p "${APP_PATH}/Contents/MacOS" "${APP_PATH}/Contents/Resources"

# Info.plist
cat > "${APP_PATH}/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>WallpaperEngineExtractor</string>
    <key>CFBundleIdentifier</key>
    <string>com.wallpaper-extractor</string>
    <key>CFBundleName</key>
    <string>Wallpaper Engine Media Extractor</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

# Main script
cat > "${APP_PATH}/Contents/MacOS/WallpaperEngineExtractor" << 'SCRIPT'
#!/bin/bash
RESOURCES="$(cd "$(dirname "$0")/../Resources" && pwd)"
if ! command -v python3 &> /dev/null; then
    osascript -e 'display dialog "Python 3 is required!\n\nInstall from: https://www.python.org/downloads/" buttons {"Download", "Cancel"}' \
        -e 'if button returned of result is "Download" then open location "https://www.python.org/downloads/"'
    exit 1
fi
cd "$RESOURCES"
exec python3 gui.py
SCRIPT
chmod +x "${APP_PATH}/Contents/MacOS/WallpaperEngineExtractor"

# Copy files
cp -R extractor gui.py run.py extractor.py "${APP_PATH}/Contents/Resources/"
cp build/icon.png "${APP_PATH}/Contents/Resources/"
mkdir -p "${APP_PATH}/Contents/Resources/input" "${APP_PATH}/Contents/Resources/outputs"

# Zip it
cd dist
zip -r "${NAME}_macOS.zip" "${NAME}.app"
cd ..

echo "  ${APP_PATH}"
echo "  ${ZIP_PATH}"
echo ""
echo "Note: This .app requires Python 3 installed on the user's Mac."
echo "For a standalone .app (no Python needed), sign up for Apple Developer"
echo "and use: bash build/build_mac_standalone.sh"
