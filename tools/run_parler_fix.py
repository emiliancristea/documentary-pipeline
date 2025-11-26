import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
import os
import json
import yaml

# Global model cache
_MODEL = None
_TOKENIZER = None
_DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

def get_parler_model():
    global _MODEL, _TOKENIZER
    if _MODEL is None:
        # Local path we downloaded to
        model_name = "models/parler-tts-mini-v1"
        if not os.path.exists(model_name):
            raise FileNotFoundError(f"Parler model not found at {model_name}")
            
        print(f"Loading Parler-TTS from {model_name} on {_DEVICE}...")
        _MODEL = ParlerTTSForConditionalGeneration.from_pretrained(model_name).to(_DEVICE)
        _TOKENIZER = AutoTokenizer.from_pretrained(model_name)
    return _MODEL, _TOKENIZER

def generate_parler_audio(text, description, output_path):
    model, tokenizer = get_parler_model()
    
    # Tokenize
    input_ids = tokenizer(description, return_tensors="pt").input_ids.to(_DEVICE)
    prompt_input_ids = tokenizer(text, return_tensors="pt").input_ids.to(_DEVICE)
    
    # Generate
    generation = model.generate(
        input_ids=input_ids, 
        prompt_input_ids=prompt_input_ids,
        do_sample=True,
        temperature=1.0
    )
    
    # Save
    audio_arr = generation.cpu().numpy().squeeze()
    sample_rate = model.config.sampling_rate
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, audio_arr, sample_rate)
    return output_path

def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    print("--- Running Parler-TTS Audio Generation ---")
    
    episode_name = "Episode_0001_Uruk"
    config = load_config()
    episode_root = os.path.join(config['project']['output_dir'], episode_name)
    tts_plan_path = os.path.join(episode_root, "tts_plan.json")
    audio_dir = os.path.join(episode_root, 'assets', 'audio')
    
    if not os.path.exists(tts_plan_path):
        print("No tts_plan.json found.")
        return

    with open(tts_plan_path, 'r') as f:
        tts_plan = json.load(f)
        
    # DEFINE THE VOICE STYLE HERE
    description = "A male narrator with a deep, grave voice speaking slowly and clearly in a historical documentary style. High quality audio."
    
    chunks = tts_plan.get('audio_chunks', [])
    total = len(chunks)
    
    print(f"Processing {total} chunks with Parler-TTS...")
    print(f"Style: {description}")
    
    for i, chunk in enumerate(chunks):
        text = chunk.get('text')
        filename = chunk.get('output_file')
        
        if not text or not filename:
            continue
            
        filename = os.path.basename(filename)
        out_path = os.path.join(audio_dir, filename)
        
        # Check if exists and valid size
        # NOTE: Since we are switching engine, we probably want to OVERWRITE existing files
        # so the voice is consistent. But if you want to resume, uncomment check.
        
        # Force overwrite for consistency:
        # pass 
        
        print(f"[{i+1}/{total}] Generating: {filename}...")
        try:
            generate_parler_audio(text, description, out_path)
            print(f"   -> Saved.")
        except Exception as e:
            print(f"   -> FAILED: {e}")
            import traceback
            traceback.print_exc()

    print("Done.")

if __name__ == "__main__":
    main()
