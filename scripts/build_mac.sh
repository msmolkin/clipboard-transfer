#!/bin/bash
# Build script for Mac Clipboard Sender
# Creates a standalone .app bundle

echo "Building Clipboard Sender for Mac..."

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Create build directory
mkdir -p dist

# Build the app
pyinstaller --onefile \
    --windowed \
    --name "ClipboardSender" \
    --icon=assets/icon.icns \
    --add-data "README.md:." \
    --hidden-import=PIL._tkinter_finder \
    src/cb_sender.py

echo ""
echo "Build complete!"
echo "Application saved to: dist/ClipboardSender.app"
echo ""
echo "To create a DMG for distribution:"
echo "  hdiutil create -volname ClipboardSender -srcfolder dist/ClipboardSender.app -ov -format UDZO dist/ClipboardSender.dmg"
