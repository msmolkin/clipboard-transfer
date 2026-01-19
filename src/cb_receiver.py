import os
import sys

# --- FIX 1: FORCE PURE PYTHON PROTOBUF ---
# This must be set BEFORE importing paddle to prevent the "Descriptors" crash on Python 3.12
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# --- FIX 2: PATH CORRECTION ---
# This ensures Python finds the library you just installed in the "User" folder
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python312\site-packages")
if user_site not in sys.path:
    sys.path.append(user_site)

# --- FIX 3: GPU ---
# This is a simple check to see if the GPU is available
USE_GPU = False

# --- IMPORTS ---
import socket
import ssl
import struct
import pyperclip
import time
import io
from PIL import Image

# Initialize PaddleOCR (Wrapped in try/except to catch loading errors)
print(f"Loading PaddleOCR...")
try:
    from paddleocr import PaddleOCR
    # 'lang=en' downloads the lightweight English model automatically.
    # We use 'use_gpu=True' to utilize a discrete graphics card.
    ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=USE_GPU)
    print("PaddleOCR Loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR LOADING PADDLE: {e}")
    print("Try running: pip install \"protobuf==3.20.2\" again if this persists.")
    ocr_engine = None

# CONFIGURATION
HOST = '0.0.0.0'
PORT = 65432
SAVE_FOLDER = "Received_Screenshots"

# Ensure save folder exists for screenshots and is writable
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)
    os.chmod(SAVE_FOLDER, 0o777)

# SSL Setup (Optional: remove 'context' lines if you want plain text)
# Ensure 'server.crt' and 'server.key' are in the same folder as this script
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
try:
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
except FileNotFoundError:
    print("WARNING: SSL Keys not found! Generate them or script will fail.")

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    global ip
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def recv_exactly(sock, n):
    """Wait until exactly n bytes are received."""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def start_paddle_server():
    bindsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    bindsocket.bind((HOST, PORT))
    bindsocket.listen(5)
    print(f"Listening securely at {get_ip_address()}:{PORT} with {"GPU" if USE_GPU else "CPU"} OCR...")
    print(f"Screenshots will be saved to {SAVE_FOLDER}")

    while True:
        newsocket, fromaddr = bindsocket.accept()
        try:
            conn = context.wrap_socket(newsocket, server_side=True)
            with conn:
                while True:
                    # 1. READ HEADER
                    header = recv_exactly(conn, 5)
                    if not header: break
                    msg_type, msg_len = struct.unpack('>BI', header)
                    
                    # 2. READ PAYLOAD
                    payload = recv_exactly(conn, msg_len)
                    if not payload: break

                    # 3. HANDLE DATA
                    if msg_type == 1: # TEXT
                        text = payload.decode('utf-8')
                        pyperclip.copy(text)
                        print(f"[Text] Copied: {text[:20]}...")

                    elif msg_type == 2: # IMAGE
                        print(f"[Image] Received {msg_len} bytes...")
                        
                        # A. Save Image to Disk
                        timestamp = int(time.time())
                        filename = f"{SAVE_FOLDER}/img_{timestamp}.png"
                        with open(filename, 'wb') as f:
                            f.write(payload)
                        print(f" -> Saved to {filename}")
                        # open folder in explorer with the file selected
                        os.startfile(filename)
                            
                        # B. Run PaddleOCR
                        if ocr_engine:
                            print(" -> Running PaddleOCR...", end="", flush=True)
                            try:
                                # ocr_engine.ocr takes the filename directly
                                result = ocr_engine.ocr(filename, cls=True)
                                
                                # Parse Result: Paddle returns [[[coords], (text, conf)], ...]
                                if result and result[0]:
                                    detected_lines = [line[1][0] for line in result[0]]
                                    extracted_text = "\n".join(detected_lines)
                                    
                                    if extracted_text.strip():
                                        pyperclip.copy(extracted_text)
                                        print(" Success!")
                                        print(f" -> Clipboard: {extracted_text[:30].replace(chr(10), ' ')}...")
                                    else:
                                        print(" No text detected.")
                                else:
                                    print(" No text detected.")

                            except Exception as e:
                                print(f"\n[OCR Error] {e}")
                        else:
                            print(" -> OCR Engine not loaded, skipping.")

        except Exception as e:
            print(f"Connection Error: {e}")

if __name__ == "__main__":
    try:
        start_paddle_server()
    except KeyboardInterrupt:
        print("Keyboard Interrupt Detected. Exiting...")