import os
import json
from agents.base import BaseAgent
from utils.google_api import generate_text, synthesize_speech

class VoiceOverAgent(BaseAgent):
    def run(self, context):
        print("--- Starting Voice-Over Agent ---")
        script = context.get('script')
        structure = context.get('structure')
        brief = context.get('brief')
        
        if not script or not structure:
            print("ERROR: Missing script or structure for VO Agent")
            return context

        system_prompt = self.load_prompt('voice_over_agent.md')
        
        input_data = {
            "metadata": {
                "title": brief.get('title'),
                "series": brief.get('series')
            },
            "script_full_text": script,
            "structure": structure
        }
        
        input_str = json.dumps(input_data, indent=2, default=str)
        
        response = generate_text(
            system_prompt=system_prompt,
            user_prompt=f"Create a TTS plan based on this script and structure:\n{input_str}",
            model_key="text_main"
        )
        
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
            
        try:
            tts_plan = json.loads(response)
            context['tts_plan'] = tts_plan
            
            with open(os.path.join(context['paths']['root'], 'tts_plan.json'), 'w') as f:
                json.dump(tts_plan, f, indent=2)
                
            # --- EXECUTION PHASE ---
            audio_dir = os.path.join(context['paths']['root'], 'assets', 'audio')
            os.makedirs(audio_dir, exist_ok=True)
            
            voice_params = self.config.get('tts', {})
            
            for chunk in tts_plan.get('audio_chunks', []):
                text = chunk.get('text')
                filename = chunk.get('output_file')
                if text and filename:
                    filename = os.path.basename(filename)
                    out_path = os.path.join(audio_dir, filename)
                    
                    # Check for existing file with likely extensions and VALIDATE SIZE
                    base_path = os.path.splitext(out_path)[0]
                    existing_file = None
                    for ext in ['.wav', '.mp3']:
                        candidate = base_path + ext
                        if os.path.exists(candidate):
                            # Check if file is valid (e.g. > 1KB)
                            if os.path.getsize(candidate) > 1024:
                                existing_file = candidate
                                break
                            else:
                                print(f"WARNING: Found corrupt/small audio file {candidate}. Deleting to regenerate.")
                                try:
                                    os.remove(candidate)
                                except Exception as e:
                                    print(f"Failed to delete {candidate}: {e}")

                    if existing_file:
                        final_path = existing_file
                    else:
                        final_path = synthesize_speech(
                            text=text, 
                            voice_params=voice_params, 
                            output_path=out_path
                        )
                    
                    chunk['absolute_path'] = final_path

        except json.JSONDecodeError:
            print("ERROR: Failed to parse JSON from VO Agent")
            
        return context
