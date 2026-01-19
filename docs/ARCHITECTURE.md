# Architecture Documentation

## System Overview

Clipboard Transfer uses a client-server architecture with SSL encryption to securely sync clipboard content from Mac to Windows over a local network.

```
┌─────────────┐                    ┌──────────────┐
│   Mac       │                    │   Windows    │
│  (Sender)   │ ──── SSL/TLS ────> │  (Receiver)  │
│             │    Port 65432      │              │
└─────────────┘                    └──────────────┘
     │                                    │
     │ Monitors Clipboard                 │ Updates Clipboard
     │ - Text                              │ - Text
     │ - Images                            │ - OCR Text
     │                                    │ Saves Images
```

## Components

### 1. Mac Sender (`src/cb_sender.py`)

**Purpose**: Monitor Mac clipboard and send changes to Windows

**Key Functions**:
- `start_sender()`: Main loop that monitors clipboard
- Clipboard monitoring via `pyperclip` and `ImageGrab`
- Duplicate detection using checksum comparison
- SSL client connection

**Data Flow**:
1. Poll clipboard every 1 second
2. Check for images first (using `ImageGrab.grabclipboard()`)
3. If no image, check for text (using `pyperclip.paste()`)
4. Compare with last sent data to avoid duplicates
5. If different, send via SSL socket

**Protocol**:
```
Header: [Type (1 byte)] [Length (4 bytes)]
Type: 1 = Text, 2 = Image
Length: Size of payload in bytes
Payload: UTF-8 text or PNG binary data
```

### 2. Windows Receiver (`src/cb_receiver.py`)

**Purpose**: Listen for incoming clipboard data and update Windows clipboard

**Key Functions**:
- `start_paddle_server()`: Main server loop
- `recv_exactly()`: Ensures complete data reception
- `get_ip_address()`: Displays server IP for configuration
- OCR text extraction from images

**Data Flow**:
1. Listen on port 65432 with SSL
2. Accept connection from Mac sender
3. Read 5-byte header to determine type and length
4. Read exact payload bytes
5. Process based on type:
   - **Text**: Copy directly to clipboard
   - **Image**: Save to disk, run OCR, copy extracted text

**OCR Pipeline**:
```
Image Received → Save to File → PaddleOCR Analysis → Extract Text → Copy to Clipboard
                      │
                      └─→ Open in Explorer
```

### 3. SSL Certificate Generator (`scripts/gen_keys.py`)

**Purpose**: Create self-signed SSL certificates for local encryption

**Process**:
1. Generate RSA 2048-bit private key
2. Create self-signed certificate valid for 10 years
3. Save as `server.key` and `server.crt`
4. Uses cryptography library

**Security Note**: Self-signed certs are acceptable for local network use where both endpoints are controlled by the same user.

## Protocol Specification

### Message Format

All messages use big-endian byte order:

```
┌────────┬───────────┬─────────────┐
│  Type  │  Length   │   Payload   │
│ 1 byte │  4 bytes  │  N bytes    │
└────────┴───────────┴─────────────┘
```

### Message Types

- `0x01`: Text message
  - Payload: UTF-8 encoded string
- `0x02`: Image message
  - Payload: PNG binary data

### Example: Sending "Hello"

```
Type:    0x01
Length:  0x00 0x00 0x00 0x05 (5 bytes)
Payload: 0x48 0x65 0x6C 0x6C 0x6F (UTF-8 "Hello")

Wire format: 01 00 00 00 05 48 65 6C 6C 6F
```

## Security Model

### Threat Model

**Protected Against**:
- Passive network eavesdropping (SSL encryption)
- Basic man-in-the-middle attacks (SSL)
- Accidental data exposure on network

**NOT Protected Against**:
- Sophisticated MITM with custom certs (self-signed cert accepted without validation)
- Compromised endpoint machines
- Network-level attacks (DDoS, packet injection)

**Recommendation**: Use only on trusted local networks (home/office)

### SSL Configuration

**Sender (Mac)**:
```python
context = ssl.create_default_context()
context.check_hostname = False  # Self-signed cert
context.verify_mode = ssl.CERT_NONE  # Trust without CA validation
```

**Receiver (Windows)**:
```python
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="server.crt", keyfile="server.key")
```

## Performance Characteristics

### CPU Usage
- **Sender (Mac)**: ~0.1-0.5% (polling only)
- **Receiver (Windows)**:
  - Idle: ~0.1%
  - OCR Processing: 25-80% (single core)
  - With GPU: 5-15%

### Memory Usage
- **Sender**: ~30-50 MB
- **Receiver**: ~200-500 MB (PaddleOCR models loaded)

### Network Bandwidth
- **Text**: Negligible (<1 KB/s average)
- **Screenshot**: 50 KB - 5 MB per transfer
- **Connection**: Single persistent TCP connection

### Latency
- Text transfer: 10-50 ms
- Image transfer: 100-500 ms (size dependent)
- OCR processing: 1-5 seconds (CPU) / 0.5-2 seconds (GPU)

## Dependencies

### Mac Dependencies
- **Pillow**: Image handling and clipboard access
- **pyperclip**: Text clipboard access
- **cryptography**: SSL certificate generation

### Windows Dependencies
- **Pillow**: Image handling
- **pyperclip**: Clipboard access
- **PaddleOCR**: Text extraction from images
- **PaddlePaddle**: Deep learning framework for OCR
- **protobuf**: Required by PaddlePaddle (pinned to 3.20.2 for compatibility)

## Error Handling

### Connection Errors
- Sender auto-reconnects every 3 seconds on connection loss
- Graceful handling of network interruptions
- Keyboard interrupt support (Ctrl+C) for clean exit

### Data Errors
- Invalid UTF-8 text: Logged and skipped
- Corrupt images: Logged, OCR skipped
- Partial receives: `recv_exactly()` ensures complete data

### OCR Errors
- Model loading failure: Receiver continues without OCR
- Runtime errors: Logged, clipboard gets image file path instead

## Future Enhancements

### Potential Features
- [ ] Bidirectional sync
- [ ] Multi-computer support (one-to-many)
- [ ] Clipboard history
- [ ] File transfer support
- [ ] Configuration GUI
- [ ] Auto-discovery on network (mDNS/Bonjour)
- [ ] Cloud relay for remote networks

### Performance Improvements
- [ ] Delta compression for large text
- [ ] Incremental image transfer
- [ ] Connection pooling
- [ ] Background OCR queue

## Testing

### Manual Test Cases
1. Small text (< 100 chars)
2. Large text (> 10 KB)
3. Screenshot with text
4. Screenshot without text
5. Multiple rapid copies
6. Network disconnection during transfer
7. Emoji and Unicode characters
8. Code snippets with special formatting

### Known Limitations
- No clipboard format preservation (e.g., RTF lost)
- One-way only (Mac → Windows)
- Single sender/receiver pair
- Requires manual IP configuration
- Images always converted to PNG
