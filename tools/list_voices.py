import os
import sys
import soundfile as sf
from kokoro_onnx import Kokoro
import numpy as np

def list_voices_and_sample():
    model_path = "models/kokoro/kokoro-v0_19.int8.onnx"
    voices_path = "models/kokoro/voices.bin"
    
    kokoro = Kokoro(model_path, voices_path)
    
    # Inspect internal voices dict if accessible, or just try known keys
    # kokoro-onnx stores voices in self.voices (dict)
    available_voices = list(kokoro.voices.keys())
    print("Available Voices:")
    print(", ".join(available_voices))
    
    test_text = "Uruk was not simply a large village. It was an explosion of complexity."
    target_voice = "am_michael"
    
    if target_voice not in available_voices:
        print(f"Warning: {target_voice} not found, defaulting to af_sky")
        target_voice = "af_sky"
        
    print(f"\nGenerating sample with voice: {target_voice}")
    samples, sample_rate = kokoro.create(test_text, voice=target_voice, speed=1.0)
    sf.write("sample_michael.wav", samples, sample_rate)
    print(f"Saved sample_michael.wav")

if __name__ == "__main__":
    list_voices_and_sample()
