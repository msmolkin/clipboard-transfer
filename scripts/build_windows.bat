@echo off
REM Build script for Windows Clipboard Receiver
REM Creates a standalone .exe

echo Building Clipboard Receiver for Windows...

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Create build directory
if not exist dist mkdir dist

REM Build the executable
pyinstaller --onefile ^
    --name "ClipboardReceiver" ^
    --icon=assets\icon.ico ^
    --add-data "README.md;." ^
    --hidden-import=paddle ^
    --hidden-import=paddleocr ^
    --collect-all paddleocr ^
    --collect-all paddle ^
    src\cb_receiver.py

echo.
echo Build complete!
echo Executable saved to: dist\ClipboardReceiver.exe
echo.
echo IMPORTANT: You must also distribute the following files:
echo   - server.crt and server.key (SSL certificates)
echo   - Or instruct users to generate them with scripts\gen_keys.py
echo.
echo To create an installer, use Inno Setup or NSIS.
pause
