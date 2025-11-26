# Documentary Pipeline - End-to-End Video Production Automation

> **PROPRIETARY CODE - NOT FOR REPRODUCTION OR USE**
> 
> This repository is a **portfolio demonstration only**. The code is proprietary and is shared solely to showcase technical skills and expertise. No license is granted for reproduction, modification, distribution, or commercial/personal use. All rights reserved.

A fully automated content production system that transforms a simple text brief into a complete, rendered video - with zero manual intervention.

## Key Skills Demonstrated

| Skill | Implementation |
|-------|----------------|
| **Python Automation** | End-to-end pipeline orchestration with modular agent architecture |
| **API Integration** | Google Vertex AI (Gemini, Imagen), Google Cloud TTS, streaming responses |
| **AI/LLM Orchestration** | Multi-agent system with prompt engineering and JSON schema enforcement |
| **Error Handling** | Exponential backoff retry logic, rate limit handling (429), graceful degradation |
| **Media Processing** | FFmpeg subprocess automation for video rendering and audio mixing |
| **File System Automation** | Dynamic directory creation, asset validation, corrupt file detection |
| **Configuration Management** | YAML-based configs with environment separation (mock/production modes) |
| **Data Transformation** | JSON parsing, schema extraction from LLM responses, state management |

## What This Project Does

**Input:** A YAML brief describing a video topic (title, key points, duration)

**Output:** A fully rendered MP4 video with:
- AI-generated script (structured narrative)
- AI-generated images for each scene
- AI-synthesized voice-over narration
- Timed video assembly with transitions

```
Brief (YAML) → Script → Structure → Images → Audio → Timeline → Video (MP4)
```

## Technical Architecture

### Pipeline Pattern (State Machine)
```python
# main.py - Sequential agent execution with shared context
pipeline = [
    ScriptAgent(config),        # LLM: Generate documentary script
    StructureTimingAgent(config), # LLM: Break into timed segments
    ImagePromptAgent(config),   # LLM: Create visual descriptions
    ProductionAgent(config),    # API: Generate images (Imagen)
    VoiceOverAgent(config),     # API: Synthesize speech (TTS)
    VideoAssemblyAgent(config), # LLM: Create timeline JSON
    QAAgent(config)             # LLM: Quality check
]

for agent in pipeline:
    context = agent.run(context)  # Each agent transforms shared state
```

### API Integration with Resilience
```python
# Exponential backoff with jitter for rate limits
@retry_with_backoff(max_retries=5, initial_delay=1.0)
def _call_api():
    return client.models.generate_content(...)

# Handles 429 RESOURCE_EXHAUSTED errors automatically
# Implements streaming responses for large media files
```

### Media Processing Automation
```python
# FFmpeg subprocess orchestration
cmd = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0", "-i", video_concat_path,
    "-f", "concat", "-safe", "0", "-i", audio_concat_path,
    "-c:v", "libx264", "-r", "30", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest", output_path
]
subprocess.run(cmd, check=True)
```

### Intelligent Asset Management
```python
# Skip regeneration if valid asset exists, detect corruption
for ext in ['.png', '.jpg', '.jpeg']:
    candidate = base_path + ext
    if os.path.exists(candidate):
        if os.path.getsize(candidate) > 1024:  # Validate file integrity
            existing_file = candidate
            break
        else:
            os.remove(candidate)  # Auto-cleanup corrupt files
```

## Project Structure

```
├── main.py                 # Pipeline orchestrator (CLI entry point)
├── agents/                 # Modular agent classes
│   ├── base.py            # Abstract base with prompt loading
│   ├── scripting.py       # Script + Structure + Image prompt agents
│   ├── production.py      # Image generation with Imagen API
│   ├── voice_over.py      # TTS synthesis with speech API
│   ├── assembly.py        # Timeline generation
│   └── qa.py              # Quality assurance checks
├── utils/
│   ├── google_api.py      # API client with retry logic & streaming
│   └── local_tts.py       # Fallback local TTS support
├── tools/
│   └── render_video.py    # FFmpeg video assembly automation
├── prompts/               # LLM system prompts (markdown)
├── config/
│   └── settings.yaml      # Centralized configuration
└── episodes/              # Output directory (generated content)
```

## Tech Stack

- **Language:** Python 3.x
- **AI/ML:** Google Vertex AI (Gemini 3 Pro, Imagen 3), Google Cloud TTS
- **Media:** FFmpeg (video encoding, audio mixing)
- **Config:** YAML, JSON
- **APIs:** Google GenAI SDK (streaming)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key in config/settings.yaml or environment
export GOOGLE_API_KEY="your-key"

# Run full pipeline (mock mode for testing)
python main.py --brief episodes/episode_0001_uruk.yaml --name Test_Episode

# Run with real AI + video render
python main.py --brief episodes/episode_0001_uruk.yaml --name My_Episode --render
```

## Automation Highlights

1. **Zero-Touch Execution** - Single command produces complete video from text input
2. **Fault Tolerance** - Automatic retries, fallback renders, corrupt file cleanup
3. **Idempotent Operations** - Re-running skips already-generated valid assets
4. **Configurable Modes** - Mock mode for development, production mode for real output
5. **Extensible Design** - Add new agents by extending `BaseAgent` class

