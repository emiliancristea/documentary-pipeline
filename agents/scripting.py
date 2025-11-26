import json
import yaml
import os
from agents.base import BaseAgent
from utils.google_api import generate_text, generate_image

class ScriptAgent(BaseAgent):
    def run(self, context):
        print("--- Starting Script Agent ---")
        brief = context['brief']
        system_prompt = self.load_prompt('script_writer_global.md')
        
        if 'series' not in brief:
            print("WARNING: No 'series' found in brief. Defaulting to 'Power, Empires & Diplomacy'")
            brief['series'] = "Power, Empires & Diplomacy"

        brief_str = yaml.dump(brief)
        
        script_content = generate_text(
            system_prompt=system_prompt,
            user_prompt=f"Here is the episode brief:\n{brief_str}",
            model_key="text_main"
        )
        
        context['script'] = script_content
        
        with open(os.path.join(context['paths']['root'], 'script.md'), 'w') as f:
            f.write(script_content)
            
        return context

class StructureTimingAgent(BaseAgent):
    def run(self, context):
        print("--- Starting Structure & Timing Agent ---")
        script = context['script']
        brief = context['brief']
        system_prompt = self.load_prompt('structure_timing_agent.md')
        
        input_data = {
            "brief": brief,
            "script_content": script
        }
        input_str = json.dumps(input_data, indent=2, default=str)

        response = generate_text(
            system_prompt=system_prompt,
            user_prompt=f"Here is the episode data. Produce the STRUCTURE OBJECT JSON:\n{input_str}",
            model_key="text_main"
        )
        
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
            
        try:
            structure = json.loads(response)
            context['structure'] = structure
            
            with open(os.path.join(context['paths']['root'], 'structure.json'), 'w') as f:
                json.dump(structure, f, indent=2)
                
        except json.JSONDecodeError:
            print("ERROR: Failed to parse JSON from Structure Agent")
            with open(os.path.join(context['paths']['root'], 'structure_error.txt'), 'w') as f:
                f.write(response)
            
        return context

class ImagePromptAgent(BaseAgent):
    def run(self, context):
        print("--- Starting Image Prompt Agent ---")
        structure = context.get('structure')
        if not structure:
             print("ERROR: No structure found for Image Prompt Agent")
             return context

        system_prompt = self.load_prompt('image_prompt_agent.md')
        
        input_str = json.dumps(structure, indent=2)
        
        response = generate_text(
            system_prompt=system_prompt,
            user_prompt=f"Generate image prompts for this structure:\n{input_str}",
            model_key="text_main"
        )
        
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
            
        try:
            image_prompts = json.loads(response)
            context['image_prompts'] = image_prompts
            
            with open(os.path.join(context['paths']['root'], 'image_prompts.json'), 'w') as f:
                json.dump(image_prompts, f, indent=2)
        except:
            print("ERROR: Failed to parse JSON from Image Prompt Agent")
            
        return context
