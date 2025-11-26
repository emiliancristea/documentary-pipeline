import os
import json
import yaml
import mimetypes
import time
import random
from google import genai
from google.genai import types

# Load config
def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)

CONFIG = load_config()

# Initialize Client
# Read API key from config instead of environment
api_key = CONFIG.get('google', {}).get('api_key')

if not api_key and not CONFIG['runtime']['mock_mode']:
    print("CRITICAL WARNING: google.api_key not found in config/settings.yaml.")

try:
    # Only initialize client if we have a key or if we might need it (though mock mode skips it)
    # We pass the key explicitly.
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        client = None
except Exception as e:
    if not CONFIG['runtime']['mock_mode']:
        print(f"Error initializing GenAI client: {e}")
    client = None

def retry_with_backoff(max_retries=5, initial_delay=1.0):
    """Decorator to retry function on 429 Resource Exhausted errors."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                        retries += 1
                        if retries == max_retries:
                            print(f"ERROR: Max retries exceeded for {func.__name__} due to rate limit.")
                            raise e
                        
                        sleep_time = delay * (1 + random.random() * 0.5) # Add jitter
                        print(f"WARNING: Rate limit hit in {func.__name__}. Retrying in {sleep_time:.2f}s... (Attempt {retries}/{max_retries})")
                        time.sleep(sleep_time)
                        delay *= 2 # Exponential backoff
                    else:
                        raise e
            return None
        return wrapper
    return decorator

def generate_text(system_prompt: str, user_prompt: str, model_key: str = "text_main") -> str:
    """
    Uses a Google text model to generate a response.
    """
    if CONFIG['runtime']['mock_mode']:
        print(f"DEBUG: [MOCK] Generating text with {model_key}...")
        return _get_mock_text_response(system_prompt)

    if not client:
        print("ERROR: Client not initialized. Check google.api_key in settings.yaml")
        return ""

    model_name = CONFIG['models'].get(model_key, "gemini-2.0-flash-exp")
    print(f"DEBUG: Calling {model_name}...")

    @retry_with_backoff(max_retries=5)
    def _call_api():
        return client.models.generate_content(
            model=model_name,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            ),
            contents=[user_prompt]
        )

    try:
        response = _call_api()
        return response.text
    except Exception as e:
        print(f"ERROR in generate_text: {e}")
        return ""

def generate_image(prompt_text: str, output_path: str, model_key: str = "image_main") -> str:
    """
    Uses a Google image generation model to create an image.
    """
    model_name = CONFIG['models'].get(model_key, "gemini-3-pro-image-preview")

    if CONFIG['runtime']['mock_mode']:
        print(f"DEBUG: [MOCK] Generating image for: {prompt_text[:30]}...")
        with open(output_path, "w") as f:
            f.write("Mock Image Data")
        return output_path

    if not client:
        print("ERROR: Client not initialized. Check google.api_key in settings.yaml")
        return ""

    print(f"DEBUG: Generating image with {model_name}...")

    @retry_with_backoff(max_retries=5, initial_delay=2.0)
    def _call_api():
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt_text)]
            )
        ]
        
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=types.ImageConfig(image_size="1K")
        )

        return client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=generate_content_config,
        )

    try:
        response_stream = _call_api()
        
        # Buffer data first to ensure valid response before opening file
        image_data = None
        final_output_path = output_path

        for chunk in response_stream:
            for part in chunk.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    image_data = part.inline_data.data
                    mime_type = part.inline_data.mime_type
                    extension = mimetypes.guess_extension(mime_type) or ".png"
                    
                    base, ext = os.path.splitext(output_path)
                    if ext.lower() != extension.lower():
                        final_output_path = base + extension
                    else:
                        final_output_path = output_path
                    break # Found data
            if image_data:
                break
        
        if not image_data:
            raise RuntimeError("No image bytes found in response stream.")

        with open(final_output_path, "wb") as f:
            f.write(image_data)
        return final_output_path
            
    except Exception as e:
        print(f"ERROR in generate_image: {e}")
        # Ensure no partial file exists if it failed late
        if os.path.exists(output_path) and os.path.getsize(output_path) == 0:
             try:
                 os.remove(output_path)
             except:
                 pass
        return ""

def synthesize_speech(text: str, voice_params: dict, output_path: str) -> str:
    """
    Uses Gemini TTS to synthesize text into audio.
    """
    model_name = CONFIG['models'].get("tts_model", "gemini-2.5-pro-preview-tts")

    if CONFIG['runtime']['mock_mode']:
        print(f"DEBUG: [MOCK] Synthesizing speech...")
        with open(output_path, "w") as f:
            f.write("Mock Audio Data")
        return output_path

    if not client:
        print("ERROR: Client not initialized. Check google.api_key in settings.yaml")
        return ""

    voice_name = voice_params.get("voice_name") or CONFIG['tts']['voice_name']
    
    print(f"DEBUG: Synthesizing speech with {model_name} (Voice: {voice_name})...")

    @retry_with_backoff(max_retries=8, initial_delay=2.0)
    def _call_api():
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=text)],
            )
        ]
        
        config = types.GenerateContentConfig(
            temperature=1,
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            ),
        )

        return client.models.generate_content_stream(
            model=model_name,
            contents=contents,
            config=config,
        )

    try:
        response_stream = _call_api()
        
        # Buffer data first
        audio_data = None
        final_output_path = output_path

        for chunk in response_stream:
            for part in chunk.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    audio_data = part.inline_data.data
                    mime_type = part.inline_data.mime_type
                    extension = mimetypes.guess_extension(mime_type)
                    
                    if extension is None:
                        extension = ".wav"
                    
                    base, ext = os.path.splitext(output_path)
                    if ext.lower() != extension.lower():
                        final_output_path = base + extension
                    else:
                        final_output_path = output_path
                    break
            if audio_data:
                break
        
        if not audio_data:
            raise RuntimeError("No audio bytes found in response stream.")

        with open(final_output_path, "wb") as f:
            f.write(audio_data)
        return final_output_path

    except Exception as e:
        print(f"ERROR in synthesize_speech: {e}")
        # Cleanup
        if os.path.exists(output_path) and os.path.getsize(output_path) == 0:
             try:
                 os.remove(output_path)
             except:
                 pass
        return ""

def _get_mock_text_response(system_prompt):
    """Helper to return context-aware mock responses."""
    if "Structure & Timing Agent" in system_prompt:
        return json.dumps({
            "episode_id": "mock_id",
            "target_duration_minutes": 15,
            "total_estimated_minutes": 14.5,
            "segments": [
                {
                    "id": "seg_01",
                    "type": "hook",
                    "start_time_sec": 0.0,
                    "end_time_sec": 10.0,
                    "narration_ref": {"from_paragraph_index": 0, "to_paragraph_index": 1},
                    "visual_slots": [{"slot_id": "seg_01_shot_01", "start_time_sec": 0.0, "end_time_sec": 10.0, "visual_concept": "Wide shot", "priority": "must_have"}]
                }
            ],
            "ad_break_suggestions": [],
            "notes_for_next_agents": ["Mock structure"]
        })
    if "Image Prompt Agent" in system_prompt:
        return json.dumps({
            "episode_id": "mock_id",
            "image_prompts": [{"slot_id": "seg_01_shot_01", "segment_id": "seg_01", "start_time_sec": 0.0, "end_time_sec": 10.0, "prompt_text": "A wide shot of Uruk.", "safety_notes": "None"}]
        })
    if "Voice-Over (TTS) Agent" in system_prompt:
        return json.dumps({
            "episode_id": "mock_id",
            "voice_profile": {"engine": "google-tts", "default_voice": "Charon"},
            "audio_chunks": [{"chunk_id": "aud_seg_01", "segment_id": "seg_01", "text": "This is Uruk.", "output_file": "audio/seg_01.wav"}]
        })
    if "Video Assembly" in system_prompt:
        return json.dumps({
            "episode_id": "mock_id",
            "frame_rate": 30,
            "tracks": {
                "video": [{"slot_id": "seg_01_shot_01", "image_file": "assets/images/seg_01_shot_01.png", "start_time_sec": 0.0, "end_time_sec": 10.0, "transition_in": "fade", "transition_out": "cut"}],
                "audio": [{"chunk_id": "aud_seg_01", "audio_file": "assets/audio/seg_01.wav", "start_time_sec": 0.0, "end_time_sec": 10.0}]
            }
        })
    if "QA" in system_prompt:
        return "# QA Report\nMock report."
    
    # Script Writer Mock
    return """
[1] EPISODE METADATA
- Title: Mock Episode
[2] SEGMENT OUTLINE
- 0:00 Hook
[3] FULL VOICE-OVER SCRIPT
This is a mock script.
[4] VISUAL SUGGESTIONS
- Mock visual.
[5] NOTES
- Mock notes.
"""
