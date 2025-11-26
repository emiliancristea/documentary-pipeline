import os
import yaml
import json
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

# Switch to Local TTS
from utils.local_tts import synthesize_speech_local

def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    print("--- Setting up Audio-Only Fix (LOCAL KOKORO TTS) ---")
    
    # Hardcoded paths based on previous context
    episode_name = "Episode_0001_Uruk"
    config = load_config()
    episode_root = os.path.join(config['project']['output_dir'], episode_name)
    tts_plan_path = os.path.join(episode_root, "tts_plan.json")
    audio_dir = os.path.join(episode_root, 'assets', 'audio')
    
    if not os.path.exists(tts_plan_path):
        print(f"CRITICAL ERROR: tts_plan.json not found at {tts_plan_path}")
        return

    print(f"Loading plan from {tts_plan_path}...")
    with open(tts_plan_path, 'r') as f:
        tts_plan = json.load(f)

    # Use a Kokoro voice instead of Google's
    # Common options: af_sky, af_bella, af_sarah, am_michael, am_adam
    voice_name = "am_michael" 
    
    chunks = tts_plan.get('audio_chunks', [])
    total = len(chunks)
    
    print(f"Found {total} chunks to verify/synthesize.")
    os.makedirs(audio_dir, exist_ok=True)

    for i, chunk in enumerate(chunks):
        text = chunk.get('text')
        filename = chunk.get('output_file')
        
        if not text or not filename:
            continue
            
        filename = os.path.basename(filename)
        out_path = os.path.join(audio_dir, filename)
        
        # --- Logic from Agent: Check Exists + Size ---
        base_path = os.path.splitext(out_path)[0]
        existing_file = None
        
        # Check typical extensions
        for ext in ['.wav', '.mp3']:
            candidate = base_path + ext
            if os.path.exists(candidate):
                size = os.path.getsize(candidate)
                if size > 1024: # 1KB threshold
                    existing_file = candidate
                    break
                else:
                    print(f"[{i+1}/{total}] Found corrupt file ({size} bytes): {os.path.basename(candidate)}. Deleting.")
                    try:
                        os.remove(candidate)
                    except Exception as e:
                        print(f"Warning: Could not delete {candidate}: {e}")

        if existing_file:
            # OPTIONAL: Force regenerate to ensure consistent voice?
            # Since we switched engines, existing files (from Google) will sound different from new ones (Kokoro).
            # Recommendation: DELETE ALL and regenerate so the voice matches.
            pass
            # print(f"[{i+1}/{total}] OK: {os.path.basename(existing_file)}")
            # continue
        
        print(f"[{i+1}/{total}] Generating (Local): {filename}...")
        
        # Call Local TTS
        result_path = synthesize_speech_local(
            text=text, 
            output_path=out_path,
            voice_name=voice_name
        )
        
        if result_path:
            print(f"   -> Success: {os.path.basename(result_path)}")
        else:
            print(f"   -> FAILED: {filename}")

    print("\n--- Audio Fix Complete ---")

if __name__ == "__main__":
    main()
