# cb_sender.py
# Sends clipboard contents to a Windows machine via SSL
# Requires Python 3.10+
# pip install Pillow pyperclip

import socket
import ssl
import struct
import pyperclip
import time
import io
from PIL import ImageGrab  # pip install Pillow

# --- CONFIGURATION ---
SERVER_IP = '192.168.1.63'
PORT = 65432

# --- SSL SETUP ---
# We tell the Mac to trust the connection without needing the certificate file
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

def start_sender():
    last_data_checksum = None  # Keeps track of what we last sent to avoid duplicates

    print(f"Creating clipboard sender client. Attempting to connect to {SERVER_IP}...")
    print("If you haven't started the receiver yet, remember to start it first and restart this client.")

    while True:
        try:
            # Create a socket and wrap it in SSL
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Set a timeout so it doesn't hang forever if Windows is off
            raw_socket.settimeout(5) 
            
            with context.wrap_socket(raw_socket, server_hostname=SERVER_IP) as s:
                s.connect((SERVER_IP, PORT))
                s.settimeout(None) # Remove timeout once connected
                print(f"Connected! clipboard syncing is active.")

                while True:
                    msg_type = 0
                    payload = b''
                    
                    # 1. CHECK FOR IMAGE FIRST
                    # ImageGrab.grabclipboard() returns an Image object if a screenshot is in clipboard
                    img = ImageGrab.grabclipboard()
                    
                    if img:
                        with io.BytesIO() as output:
                            # Convert raw image to PNG bytes
                            img.save(output, format="PNG")
                            payload = output.getvalue()
                            msg_type = 2  # 2 = Image
                    
                    # 2. IF NO IMAGE, CHECK FOR TEXT
                    else:
                        text = pyperclip.paste()
                        if text:
                            payload = text.encode('utf-8')
                            msg_type = 1  # 1 = Text

                    # 3. SEND LOGIC
                    # Only send if we have data AND it's different from the last thing we sent
                    if payload and payload != last_data_checksum:
                        last_data_checksum = payload 

                        # Protocol: [Type (1 byte)] + [Length (4 bytes)]
                        header = struct.pack('>BI', msg_type, len(payload))
                        
                        s.sendall(header + payload)
                        
                        if msg_type == 1:
                            print(f"Sent Text: {len(payload)} bytes")
                        elif msg_type == 2:
                            print(f"Sent Image: {len(payload)} bytes")
                    
                    # Sleep briefly to save CPU
                    time.sleep(1.0)

        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            print(f"Connection lost or failed. Retrying in 3 seconds... ({e})")
            try:
                time.sleep(3)
            except KeyboardInterrupt:
                print("\nFailed to connect. Keyboard interrupt received. Stopping sender.")
                break
        except KeyboardInterrupt:
            print("\nStopping sender.")
            break

if __name__ == "__main__":
    start_sender()