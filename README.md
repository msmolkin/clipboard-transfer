# Clipboard Transfer

**Unidirectional clipboard sync from Mac to Windows over local network**

Transfer text and images from your Mac's clipboard directly to your Windows machine automatically. Copy something on your Mac, and it instantly appears on your Windows clipboard - with OCR support for extracting text from screenshots.

## Features

- **Real-time Sync**: Automatically sends clipboard content from Mac to Windows
- **Text Support**: Copy any text on Mac, paste immediately on Windows
- **Image Support**: Screenshots and images transfer seamlessly
- **OCR Technology**: Automatically extracts text from screenshots using PaddleOCR
- **SSL Encryption**: Secure communication between devices
- **Auto-Save**: Screenshots are automatically saved and opened on Windows
- **Lightweight**: Minimal CPU usage with smart duplicate detection

## How It Works

1. **Mac (Sender)**: Monitors clipboard for changes
2. **Secure Transfer**: Sends data over SSL-encrypted connection
3. **Windows (Receiver)**: Receives data and updates clipboard
4. **Smart OCR**: If image contains text, extracts it to clipboard
5. **Auto-Organization**: Saves all screenshots to organized folder

## Requirements

### Mac (Sender)
- macOS (tested on macOS 14+)
- Python 3.10 or higher
- Local network connection

### Windows (Receiver)
- Windows 10/11
- Python 3.12 or higher
- Local network connection
- Optional: NVIDIA GPU for faster OCR

## Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/msmolkin/clipboard-transfer.git
cd clipboard-transfer
```

### Step 2: Install Dependencies

**On Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-mac.txt
```

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-windows.txt
```

### Step 3: Generate SSL Certificates

**On Windows (run this first):**
```bash
python scripts/gen_keys.py
```

This creates `server.crt` and `server.key` in the project root.

### Step 4: Configure IP Address

**On Windows**, find your IP address:
```powershell
(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias *Wi-Fi*).IPAddress
```
Or use:
```bash
ipconfig
```
Look for "IPv4 Address" (e.g., `192.168.1.63`)

**On Mac**, edit `src/cb_sender.py` line 15:
```python
SERVER_IP = '192.168.1.63'  # Replace with your Windows IP
```

## Usage

### Start Receiver (Windows)
```bash
python src/cb_receiver.py
```

You should see:
```
Listening securely at 192.168.1.63:65432 with CPU OCR...
Screenshots will be saved to Received_Screenshots
```

### Start Sender (Mac)
```bash
python src/cb_sender.py
```

You should see:
```
Connected! clipboard syncing is active.
```

Now copy anything on your Mac and it will appear on Windows!

## Features in Detail

### Text Transfer
- Copy any text on Mac
- Instantly available on Windows clipboard
- Handles large text (essays, code, etc.)

### Image Transfer with OCR
1. Take screenshot on Mac (Cmd+Shift+4)
2. Image is sent to Windows
3. Auto-saved to `Received_Screenshots/` folder
4. Screenshot opens automatically in Windows
5. If text is detected, extracted text replaces image in clipboard
6. Paste extracted text anywhere on Windows

### Security
- All data encrypted with SSL/TLS
- Self-signed certificates for local network use
- No data leaves your local network
- No cloud services or external servers

## Troubleshooting

### "Connection Refused" on Mac
- Make sure Windows receiver is running first
- Check that SERVER_IP matches Windows IP address
- Verify both computers are on the same network
- Check Windows firewall allows port 65432

### SSL Certificate Errors
- Regenerate certificates using `python scripts/gen_keys.py`
- Make sure `server.crt` and `server.key` are in the project root folder

### OCR Not Working
- PaddleOCR downloads models on first run (this may take time)
- Check internet connection for model download
- For GPU support, ensure CUDA is installed

### Images Not Transferring
- Verify Pillow is installed on both machines
- Check screenshot folder permissions on Windows

## Advanced Configuration

### Change Port
Edit both files and change `PORT = 65432` to your preferred port.

### Disable OCR
In `src/cb_receiver.py`, set:
```python
ocr_engine = None
```

### Enable GPU OCR (Windows)
In `src/cb_receiver.py` line 16, set:
```python
USE_GPU = True
```
Requires NVIDIA GPU and CUDA installation.

## Building Executables

### Mac App
```bash
./scripts/build_mac.sh
```
Or manually:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ClipboardSender src/cb_sender.py
```

### Windows Exe
```bash
scripts\build_windows.bat
```
Or manually:
```bash
pip install pyinstaller
pyinstaller --onefile --name ClipboardReceiver src/cb_receiver.py
```

## Project Structure

```
clipboard-transfer/
├── src/
│   ├── cb_sender.py           # Mac clipboard sender
│   └── cb_receiver.py         # Windows clipboard receiver
├── scripts/
│   ├── gen_keys.py            # SSL certificate generator
│   ├── build_mac.sh           # Mac build script
│   └── build_windows.bat      # Windows build script
├── docs/
│   ├── SETUP.md               # Detailed setup guide
│   ├── ARCHITECTURE.md        # Technical documentation
│   └── check_gpu.py           # GPU testing utility
├── requirements-mac.txt       # Mac dependencies
├── requirements-windows.txt   # Windows dependencies
├── README.md
├── LICENSE
└── .gitignore
```

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Author

Created by Michael Smolkin

## Acknowledgments

- Built with [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for text extraction
- Uses [pyperclip](https://github.com/asweigart/pyperclip) for clipboard access
- SSL security via Python's cryptography library
