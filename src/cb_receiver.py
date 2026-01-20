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
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FOLDER = os.path.join(SCRIPT_DIR, "Received_Screenshots")

# Ensure save folder exists for screenshots and is writable
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)
    os.chmod(SAVE_FOLDER, 0o777)

def generate_ssl_certificates():
    """Generate self-signed SSL certificates if they don't exist."""
    print("Generating SSL certificates...")
    try:
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization, hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime

        # Generate Private Key
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Generate Self-Signed Certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(x509.NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, u"NY"),
            x509.NameAttribute(x509.NameOID.LOCALITY_NAME, u"New York"),
            x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, u"Clipboard Transfer"),
            x509.NameAttribute(x509.NameOID.COMMON_NAME, u"localhost"),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=3650)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
        ).sign(key, hashes.SHA256(), default_backend())

        # Write server.key
        with open("server.key", "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

        # Write server.crt
        with open("server.crt", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        print("✓ SSL certificates generated successfully!")
        return True

    except Exception as e:
        print(f"ERROR generating SSL certificates: {e}")
        print("Please install cryptography: pip install cryptography")
        return False

# SSL Setup - Auto-generate certificates if they don't exist
if not os.path.exists("server.crt") or not os.path.exists("server.key"):
    print("SSL certificates not found. Generating new certificates...")
    if not generate_ssl_certificates():
        sys.exit(1)

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
try:
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
except FileNotFoundError:
    print("ERROR: SSL certificate loading failed!")
    sys.exit(1)

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
    print(f"Listening securely at {get_ip_address()}:{PORT} with {'GPU' if USE_GPU else 'CPU'} OCR...")
    print(f"Screenshots will be saved to {os.path.abspath(SAVE_FOLDER)}")

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
                        filename = os.path.join(SAVE_FOLDER, f"img_{timestamp}.png")
                        try:
                            with open(filename, 'wb') as f:
                                f.write(payload)
                            print(f" -> Saved to {filename}")
                        except OSError as e:
                            print(f"[File Error] {e} (path: {filename})")
                            continue

                        # Open Explorer with the file selected (Windows only)
                        try:
                            os.system(f'explorer /select,"{os.path.abspath(filename)}"')
                        except Exception as e:
                            print(f"[File Error] {e} (path: {filename})")
                            
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
            # Keep the wording, but if a file path is present, also show the resolved absolute path.
            if isinstance(e, FileNotFoundError) and getattr(e, "filename", None):
                missing = e.filename
                resolved = os.path.abspath(missing)
                print(f"Connection Error: {e} (path: {resolved})")
            else:
                print(f"Connection Error: {e}")

if __name__ == "__main__":
    try:
        start_paddle_server()
    except KeyboardInterrupt:
        print("Keyboard Interrupt Detected. Exiting...")