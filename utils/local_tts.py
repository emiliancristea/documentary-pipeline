import os
import soundfile as sf
from kokoro_onnx import Kokoro
import json

# Initialize Kokoro once (global singleton to avoid reloading model)
_KOKORO = None
_VOICES = None

def get_kokoro():
    global _KOKORO
    if _KOKORO is None:
        # Use the int8 model which is smaller and less prone to pickle confusion if that was the issue
        model_path = os.path.join("models", "kokoro", "kokoro-v0_19.int8.onnx")
        voices_path = os.path.join("models", "kokoro", "voices.bin")
        
        if not os.path.exists(model_path):
             # Fallback to full fp32 if int8 missing
             model_path = os.path.join("models", "kokoro", "kokoro-v0_19.onnx")
        
        if not os.path.exists(model_path) or not os.path.exists(voices_path):
            raise FileNotFoundError(f"Kokoro model not found at {model_path}. Run tools/setup_kokoro.py")
            
        print(f"Loading Kokoro model from {model_path}...")
        # Explicitly use GPU if available
        _KOKORO = Kokoro(model_path, voices_path)
    return _KOKORO

def synthesize_speech_local(text: str, output_path: str, voice_name: str = "af_sky", speed: float = 1.0) -> str:
    """
    Synthesizes speech using local Kokoro ONNX model.
    """
    try:
        kokoro = get_kokoro()
        
        # Ensure output dir exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate audio
        # Kokoro ONNX returns (samples, sample_rate)
        samples, sample_rate = kokoro.create(
            text, 
            voice=voice_name, 
            speed=speed, 
            lang="en-us"
        )
        
        # Save to file
        sf.write(output_path, samples, sample_rate)
        return output_path
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR in local TTS: {e}")
        return ""
