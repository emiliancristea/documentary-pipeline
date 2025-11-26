import os
import sys
import soundfile as sf
from kokoro_onnx import Kokoro

# Ensure we are in the right directory context if run from root
if not os.path.exists("models"):
    print("ERROR: Run this from the project root (where 'models' dir exists).")
    sys.exit(1)

def test_local_tts():
    print("--- Testing Local Kokoro TTS ---")
    
    model_path = "models/kokoro/kokoro-v0_19.int8.onnx"
    voices_path = "models/kokoro/voices.bin"
    output_path = "test_kokoro.wav"
    
    if not os.path.exists(model_path):
        print(f"Missing model: {model_path}")
        return
    if not os.path.exists(voices_path):
        print(f"Missing voices: {voices_path}")
        return
        
    print(f"Loading model: {model_path}")
    print(f"Loading voices: {voices_path}")
    
    try:
        kokoro = Kokoro(model_path, voices_path)
        print("Model loaded successfully!")
        
        text = "The walls of Uruk were not just mud brick fortifications; they were a statement of power, a visible boundary between the chaotic wild and the ordered civilization within. Gilgamesh, the legendary king, is said to have built these very walls, looking out over the fertile crescent with eyes that had seen the ends of the earth. In the bustling streets below, scribes pressed reeds into wet clay, inventing the very concept of written history, forever changing the destiny of mankind."
        print(f"Generating audio for: '{text[:30]}...'")
        
        samples, sample_rate = kokoro.create(
            text, 
            voice="am_adam", 
            speed=0.9, 
            lang="en-us"
        )
        
        output_path = "kokoro_sample_male.wav"
        sf.write(output_path, samples, sample_rate)
        print(f"Success! Audio saved to {output_path}")
        print(f"Sample rate: {sample_rate}, Samples: {len(samples)}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_local_tts()
