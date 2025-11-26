import os
from agents.base import BaseAgent
from utils.google_api import generate_image

class ProductionAgent(BaseAgent):
    def run(self, context):
        print("--- Starting Production Agent ---")
        image_prompts_data = context.get('image_prompts')
        
        if not image_prompts_data:
             print("WARNING: No image prompts found for Production Agent")
             return context

        image_prompts = image_prompts_data.get('image_prompts', [])
        
        # Create asset directories
        img_dir = os.path.join(context['paths']['root'], 'assets', 'images')
        os.makedirs(img_dir, exist_ok=True)
        
        for i, segment in enumerate(image_prompts):
            seg_id = segment.get('slot_id', str(i))
            
            if 'prompt_text' in segment:
                img_path = os.path.join(img_dir, f"{seg_id}.png")
                
                # Check for likely extensions to avoid re-generating and VALIDATE SIZE
                base_path = os.path.splitext(img_path)[0]
                existing_file = None
                for ext in ['.png', '.jpg', '.jpeg']:
                    candidate = base_path + ext
                    if os.path.exists(candidate):
                        if os.path.getsize(candidate) > 1024:
                            existing_file = candidate
                            break
                        else:
                            print(f"WARNING: Found corrupt/small image file {candidate}. Deleting to regenerate.")
                            try:
                                os.remove(candidate)
                            except Exception as e:
                                print(f"Failed to delete {candidate}: {e}")
                
                if existing_file:
                    final_path = existing_file
                else:
                    # If not exists, generate. generate_image returns the actual path used.
                    final_path = generate_image(
                        prompt_text=segment['prompt_text'], 
                        output_path=img_path,
                        model_key="image_main"
                    )
                
                segment['image_path'] = final_path
                
        context['image_prompts'] = image_prompts_data
        return context
