import os
import yaml
from google import genai
from google.genai import types

def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)

def test_key():
    config = load_config()
    api_key = config.get('google', {}).get('api_key')
    
    print(f"Testing API Key: {api_key[:5]}...{api_key[-5:]}")
    client = genai.Client(api_key=api_key)
    
    # 1. Test Standard Model (Cheap/Fast)
    print("\n1. Testing gemini-1.5-flash (Text)...")
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Hello, verify my billing status."
        )
        print("   SUCCESS! Text generation worked.")
        print(f"   Response snippet: {response.text[:50]}...")
    except Exception as e:
        print(f"   FAILED: {e}")

    # 3. Test Gemini 3 Pro for Audio
    print("\n3. Testing gemini-3-pro-preview (Audio)...")
    try:
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=[types.Content(
                role="user",
                parts=[types.Part.from_text(text="This is a test of audio generation.")]
            )],
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Charon"
                        )
                    )
                )
            )
        )
        # Check if we actually got audio data
        has_audio = False
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("audio"):
                    has_audio = True
                    break
        
        if has_audio:
            print("   SUCCESS! gemini-3-pro-preview generated audio.")
        else:
            print("   FAILED: Model accepted request but returned no audio data.")
            
    except Exception as e:
        print(f"   FAILED: {e}")

if __name__ == "__main__":
    test_key()
