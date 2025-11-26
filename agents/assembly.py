import os
import json
from agents.base import BaseAgent
from utils.google_api import generate_text

class VideoAssemblyAgent(BaseAgent):
    def run(self, context):
        print("--- Starting Video Assembly Agent ---")
        structure = context.get('structure')
        image_prompts = context.get('image_prompts')
        tts_plan = context.get('tts_plan')
        
        if not structure or not image_prompts or not tts_plan:
            print("ERROR: Missing upstream data for Assembly Agent")
            return context
            
        system_prompt = self.load_prompt('video_assembly_agent.md')
        
        input_data = {
            "structure": structure,
            "image_prompts": image_prompts,
            "tts_plan": tts_plan
        }
        
        input_str = json.dumps(input_data, indent=2, default=str)
        
        response = generate_text(
            system_prompt=system_prompt,
            user_prompt=f"Create a video timeline plan:\n{input_str}",
            model_key="text_main"
        )
        
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
            
        try:
            timeline = json.loads(response)
            context['timeline'] = timeline
            
            with open(os.path.join(context['paths']['root'], 'timeline.json'), 'w') as f:
                json.dump(timeline, f, indent=2)
                
        except json.JSONDecodeError:
            print("ERROR: Failed to parse JSON from Assembly Agent")
            
        return context
