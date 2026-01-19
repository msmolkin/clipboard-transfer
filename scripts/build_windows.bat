@echo off
REM Build script for Windows Clipboard Receiver
REM Creates a standalone .exe

setlocal

echo Building Clipboard Receiver for Windows...

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist\ClipboardReceiver.exe del /q dist\ClipboardReceiver.exe
if exist ClipboardReceiver.spec del /q ClipboardReceiver.spec

REM Create build directory
if not exist dist mkdir dist

REM Build the executable
echo Building executable...
pyinstaller --onefile ^
    --name "ClipboardReceiver" ^
    --add-data "README.md;." ^
    --hidden-import=paddle ^
    --hidden-import=paddleocr ^
    --collect-all paddleocr ^
    --collect-all paddle ^
    src\cb_receiver.py

echo.
echo ✓ Build complete!
echo   Executable: dist\ClipboardReceiver.exe
echo.
echo IMPORTANT: First-time users must generate SSL certificates:
echo   python scripts\gen_keys.py
echo.
echo Upload ClipboardReceiver.exe to GitHub releases
pause
