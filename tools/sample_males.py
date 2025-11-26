import os
import sys
import soundfile as sf
from kokoro_onnx import Kokoro

def sample_all_males():
    model_path = "models/kokoro/kokoro-v0_19.int8.onnx"
    voices_path = "models/kokoro/voices.bin"
    kokoro = Kokoro(model_path, voices_path)
    
    text = "To the ancient Mesopotamians, the defining feature of civilization was not gold or armies; it was the city itself."
    
    male_voices = ["am_adam", "am_michael", "bm_george", "bm_lewis"]
    
    print(f"Generating samples for text: '{text}'\n")
    
    for voice in male_voices:
        print(f"Generating {voice}...")
        samples, sample_rate = kokoro.create(text, voice=voice, speed=1.0, lang="en-us")
        filename = f"sample_{voice}.wav"
        sf.write(filename, samples, sample_rate)
        print(f" -> Saved {filename}")

if __name__ == "__main__":
    sample_all_males()
