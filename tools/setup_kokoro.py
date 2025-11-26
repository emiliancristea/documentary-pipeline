import os
import urllib.request
import sys

def download_file(url, dest_path):
    print(f"Downloading {url} -> {dest_path}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print("Done.")
    except Exception as e:
        print(f"Failed to download: {e}")
        sys.exit(1)

def setup_kokoro():
    model_dir = os.path.join("models", "kokoro")
    os.makedirs(model_dir, exist_ok=True)
    
    # Try the int8 quantized model which is standard for ONNX runtime usually
    onnx_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.int8.onnx"
    # voices.bin is required by kokoro-onnx v0.4.9+ (it uses np.load)
    voices_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin"
    
    onnx_path = os.path.join(model_dir, "kokoro-v0_19.int8.onnx")
    voices_path = os.path.join(model_dir, "voices.bin")
    
    if not os.path.exists(onnx_path):
        download_file(onnx_url, onnx_path)
    else:
        print(f"Model already exists at {onnx_path}")
        
    if not os.path.exists(voices_path):
        download_file(voices_url, voices_path)
    else:
        print(f"Voices file already exists at {voices_path}")

if __name__ == "__main__":
    setup_kokoro()
