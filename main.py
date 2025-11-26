import argparse
import yaml
import os
import sys
from agents.scripting import ScriptAgent, StructureTimingAgent, ImagePromptAgent
from agents.production import ProductionAgent
from agents.voice_over import VoiceOverAgent
from agents.assembly import VideoAssemblyAgent
from agents.qa import QAAgent
from tools.render_video import render_video

def load_config():
    with open("config/settings.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="KNOW: HISTORY Pipeline")
    parser.add_argument("--brief", required=True, help="Path to the episode brief YAML")
    parser.add_argument("--name", required=True, help="Internal name for the episode (no spaces)")
    parser.add_argument("--render", action="store_true", help="Render final video (requires FFmpeg and real assets)")
    args = parser.parse_args()

    config = load_config()
    
    # 1. Setup Episode Context
    episode_root = os.path.join(config['project']['output_dir'], args.name)
    os.makedirs(episode_root, exist_ok=True)
    
    print(f"Initializing Episode: {args.name}")
    print(f"Output Directory: {episode_root}")
    
    # Load Brief
    with open(args.brief, 'r') as f:
        brief_data = yaml.safe_load(f)
        
    context = {
        "name": args.name,
        "brief": brief_data,
        "config": config,
        "paths": {
            "root": episode_root,
            "prompts": config['paths']['prompts']
        }
    }
    
    # 2. Run Pipeline
    pipeline = [
        ScriptAgent(config),
        StructureTimingAgent(config),
        ImagePromptAgent(config),
        ProductionAgent(config),
        VoiceOverAgent(config),
        VideoAssemblyAgent(config),
        QAAgent(config)
    ]
    
    for agent in pipeline:
        try:
            context = agent.run(context)
        except Exception as e:
            print(f"CRITICAL ERROR in {agent.__class__.__name__}: {e}")
            sys.exit(1)
            
    # 3. Render (Optional)
    if args.render:
        if config['runtime']['mock_mode']:
            print("WARNING: Render requested but mock_mode is TRUE. Assets will be placeholders.")
        
        print("\n--- Starting Video Render ---")
        try:
            render_video(args.name, config['project']['output_dir'])
        except Exception as e:
            print(f"Render failed: {e}")

    print("\n========================================")
    print("Pipeline Complete!")
    print(f"Check {episode_root} for results.")
    print("========================================")

if __name__ == "__main__":
    main()
