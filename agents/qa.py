import os
import json
from agents.base import BaseAgent
from utils.google_api import generate_text

class QAAgent(BaseAgent):
    def run(self, context):
        print("--- Starting QA Agent ---")
        brief = context.get('brief')
        script = context.get('script')
        structure = context.get('structure')
        
        system_prompt = self.load_prompt('qa_agent.md')
        
        input_data = {
            "brief": brief,
            "script": script,
            "structure": structure
        }
        
        input_str = json.dumps(input_data, indent=2, default=str)
        
        response = generate_text(
            system_prompt=system_prompt,
            user_prompt=f"Review this episode data and produce a QA report:\n{input_str}",
            model_key="text_main"
        )
        
        context['qa_report'] = response
        
        with open(os.path.join(context['paths']['root'], 'qa_report.md'), 'w') as f:
            f.write(response)
            
        return context
