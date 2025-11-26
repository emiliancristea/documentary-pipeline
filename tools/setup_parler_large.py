import os
from huggingface_hub import snapshot_download

def setup_parler_large():
    model_id = "parler-tts/parler-tts-large-v1"
    output_dir = "models/parler-tts-large-v1"
    
    print(f"Downloading {model_id} to {output_dir}...")
    
    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Download all files
    snapshot_download(
        repo_id=model_id,
        local_dir=output_dir,
        local_dir_use_symlinks=False
    )
    
    print(f"\nSuccess! Model downloaded to: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    setup_parler_large()
