# Setup Guide

## Quick Start

### Windows Setup (Receiver)

1. **Install Python 3.12+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Check "Add Python to PATH" during installation

2. **Install Dependencies**
   ```bash
   cd clipboard-transfer
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements-windows.txt
   ```

3. **Find Your IP Address** (SSL certificates auto-generate on first run)
   ```powershell
   (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias *Wi-Fi*).IPAddress
   ```
   Or use:
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" under your active network adapter (e.g., `192.168.1.63`)

5. **Allow Firewall Access**
   - Windows may prompt to allow Python network access
   - Click "Allow access"
   - Or manually add firewall rule for port 65432

### Mac Setup (Sender)

1. **Install Python 3.10+**
   - macOS usually comes with Python 3
   - Or install via Homebrew: `brew install python3`

2. **Install Dependencies**
   ```bash
   cd clipboard-transfer
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements-mac.txt
   ```

3. **Configure Windows IP**
   - Edit `src/cb_sender.py`
   - Line 15: Change `SERVER_IP` to your Windows IP address
   ```python
   SERVER_IP = '192.168.1.63'  # Your Windows IP here
   ```

## Running the Application

### Start Receiver First (Windows)
```bash
cd clipboard-transfer
.venv\Scripts\activate
python src/cb_receiver.py
```

Expected output:
```
Loading PaddleOCR...
PaddleOCR Loaded successfully.
Listening securely at 192.168.1.63:65432 with CPU OCR...
Screenshots will be saved to Received_Screenshots
```

### Start Sender (Mac)
```bash
cd clipboard-transfer
source .venv/bin/activate
python src/cb_sender.py
```

Expected output:
```
Creating clipboard sender client. Attempting to connect to 192.168.1.63...
Connected! clipboard syncing is active.
```

## Testing

1. **Test Text**: Copy text on Mac, paste on Windows
2. **Test Image**: Take screenshot on Mac (Cmd+Shift+4), check Windows clipboard

## Common Issues

### "Connection Refused"
- Start Windows receiver first, then Mac sender
- Verify IP address in `cb_sender.py` matches Windows IP
- Check both devices on same WiFi network
- Disable VPN if active

### "Module not found"
- Activate virtual environment first
- Reinstall dependencies: `pip install -r requirements-xxx.txt`

### OCR Not Working
- First run downloads AI models (may take 5-10 minutes)
- Requires internet connection for initial model download
- Models cached locally after first download

### SSL Errors
- Delete `server.crt` and `server.key` and restart receiver
- Certificates auto-generate on first run
- Manually generate with `python scripts/gen_keys.py` if needed

## Network Configuration

### Different Subnets
If Mac and Windows are on different subnets, you'll need:
- VPN or network bridge
- Or configure router to allow cross-subnet communication

### Port Forwarding
Not needed for local network use. Only needed if you want to use across the internet (not recommended for security).

## Performance Tips

### Windows GPU Acceleration
If you have NVIDIA GPU:
1. Install [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
2. Edit `src/cb_receiver.py` line 16:
   ```python
   USE_GPU = True
   ```
3. Restart receiver

### Reduce CPU Usage
OCR is CPU-intensive. To disable:
1. Edit `src/cb_receiver.py` line 33:
   ```python
   ocr_engine = None
   ```
2. Images will save but won't extract text

## Automatic Startup

### Windows (Start on Boot)
Create batch file `start_receiver.bat`:
```batch
@echo off
cd C:\path\to\clipboard-transfer
call .venv\Scripts\activate
python src\cb_receiver.py
pause
```
Add to Windows Startup folder: `Win+R` → `shell:startup`

### Mac (Start on Login)
Create shell script `start_sender.sh`:
```bash
#!/bin/bash
cd ~/path/to/clipboard-transfer
source .venv/bin/activate
python src/cb_sender.py
```
Make executable: `chmod +x start_sender.sh`
Add to System Preferences → Users & Groups → Login Items
