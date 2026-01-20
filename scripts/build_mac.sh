#!/bin/bash
# Build script for Mac Clipboard Sender
# Creates a standalone .app bundle and DMG

set -e  # Exit on error

echo "Building Clipboard Sender for Mac..."

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist *.spec

# Create build directory
mkdir -p dist

# Build the app
echo "Building .app bundle..."
python3 -m PyInstaller --onefile \
    --windowed \
    --name "ClipboardSender" \
    --add-data "README.md:." \
    --hidden-import=PIL._tkinter_finder \
    src/cb_sender.py

echo ""
echo "Creating DMG for distribution..."
hdiutil create \
    -volname "Clipboard Sender" \
    -srcfolder dist/ClipboardSender.app \
    -ov \
    -format UDZO \
    dist/ClipboardSender.dmg

echo ""
echo "✓ Build complete!"
echo "  App:  dist/ClipboardSender.app"
echo "  DMG:  dist/ClipboardSender.dmg"
echo ""
echo "Upload ClipboardSender.dmg to GitHub releases"
