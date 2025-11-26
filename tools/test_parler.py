import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
import os

def test_parler():
    print("--- Testing Parler-TTS ---")
    
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    # Force check CUDA
    if not torch.cuda.is_available():
        print("WARNING: CUDA not found, falling back to CPU. This will be slow.")
    else:
        print(f"CUDA Detected: {torch.cuda.get_device_name(0)}")
    print(f"Using device: {device}")
    
    # Using Large v1
    model_name = "models/parler-tts-large-v1"
    
    if not os.path.exists(model_name):
        print(f"ERROR: Model path {model_name} does not exist.")
        return

    print(f"Loading model: {model_name}...")
    model = ParlerTTSForConditionalGeneration.from_pretrained(model_name).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Prompt defining the voice style
    description = "A professional male narrator with a rich, authoritative, and deep baritone voice. He speaks with a slow, measured pace suitable for a premium history documentary. The tone is grave and captivating, with perfect enunciation and a dramatic delivery that emphasizes the grandeur of the ancient world. High fidelity, studio quality recording, very clear audio."
    
    text = "The walls of Uruk were not just mud brick fortifications; they were a statement of power, a visible boundary between the chaotic wild and the ordered civilization within. Gilgamesh, the legendary king, is said to have built these very walls, looking out over the fertile crescent with eyes that had seen the ends of the earth. In the bustling streets below, scribes pressed reeds into wet clay, inventing the very concept of written history, forever changing the destiny of mankind."
    
    print(f"Generating audio for: '{text[:30]}...'")
    print(f"Style: '{description}'")
    
    input_ids = tokenizer(description, return_tensors="pt").input_ids.to(device)
    prompt_input_ids = tokenizer(text, return_tensors="pt").input_ids.to(device)
    
    generation = model.generate(
        input_ids=input_ids, 
        prompt_input_ids=prompt_input_ids,
        do_sample=True,
        temperature=1.0
    )
    
    audio_arr = generation.cpu().numpy().squeeze()
    sample_rate = model.config.sampling_rate
    
    print(f"Audio Stats: Min={audio_arr.min()}, Max={audio_arr.max()}, Mean={audio_arr.mean()}")
    print(f"Audio Shape: {audio_arr.shape}")
    print(f"Sampling Rate: {sample_rate}")
    
    output_file = "parler_sample_male_large.wav"
    sf.write(output_file, audio_arr, sample_rate)
    print(f"Saved {output_file}")

if __name__ == "__main__":
    test_parler()
