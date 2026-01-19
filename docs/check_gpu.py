import sys
import os

# --- PATH & PROTOBUF FIXES ---
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python312\site-packages")
if user_site not in sys.path:
    sys.path.append(user_site)
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# --- MAIN TEST ---
try:
    import paddle
    from paddleocr import PaddleOCR

    # 1. Force the Global Device to GPU (This replaces the old use_gpu argument)
    paddle.device.set_device('gpu')
    print(f"[CHECK] Global Device set to: {paddle.device.get_device()}")

    # 2. Load Model (Updated arguments for v3.x)
    print("[CHECK] Attempting to load OCR model on GPU...")
    
    # use_gpu=True REMOVED (It is implicit now)
    # use_angle_cls -> use_textline_orientation (Updated name)
    ocr = PaddleOCR(use_textline_orientation=True, lang='en')
    
    print("\n[SUCCESS] PaddleOCR loaded on your MX550. You are ready.")

except Exception as e:
    print(f"\n[FAILURE] {e}")