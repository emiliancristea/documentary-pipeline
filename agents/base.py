import yaml
import os

class BaseAgent:
    def __init__(self, config):
        self.config = config
    
    def load_prompt(self, prompt_name):
        path = os.path.join(self.config['paths']['prompts'], prompt_name)
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def run(self, context):
        raise NotImplementedError
