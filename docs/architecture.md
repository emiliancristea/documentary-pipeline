# System Architecture

## Data Flow

The pipeline operates on a central `EpisodeContext` object (or dictionary) that is enriched at each step.

### 1. Input Phase
**Input:** `brief.yaml` (User provided)
- Topic
- Core Thesis
- Key Historical Points
- Tone Adjustments

### 2. Scripting Phase
**Agent:** `ScriptAgent`
**Model:** Gemini Pro 1.5
**Input:** `brief.yaml` + `prompts/script_writer.md`
**Output:** `script.md`
- A full Markdown formatted script with sections (Intro, Body Paragraphs, Conclusion).
- Includes "Visual Notes" as comments or sidebars.

### 3. Structuring Phase
**Agent:** `StructureAgent`
**Model:** Gemini Pro 1.5
**Input:** `script.md` + `prompts/structure_agent.md`
**Output:** `segments.json`
- A list of objects:
  ```json
  [
    {
      "id": 1,
      "text": "In the year 1177 BC, civilization collapsed.",
      "estimated_duration": 3.5,
      "visual_intent": "Map of the Mediterranean showing burning cities."
    }
  ]
  ```

### 4. Visual Design Phase
**Agent:** `VisualPromptAgent`
**Model:** Gemini Pro 1.5 (Vision/Multimodal capable if needed for reference)
**Input:** `segments.json` + `prompts/visual_director.md`
**Output:** `visual_plan.json`
- Enriches `segments.json` with specific `image_prompt` fields optimized for Imagen.
- "A photorealistic, cinematic wide shot of a burning bronze age citadel, night time, embers in the air, 8k resolution."

### 5. Production Phase (Parallel)
**Agent:** `ImageGenAgent`
**Model:** Imagen 3
**Input:** `visual_plan.json`
**Output:** Saves images to `episodes/<id>/assets/images/001.png`, etc.

**Agent:** `TTSAgent`
**Model:** Google Cloud TTS (Journey or Studio voices)
**Input:** `visual_plan.json` (text fields)
**Output:** Saves audio to `episodes/<id>/assets/audio/001.mp3`

### 6. Assembly Phase
**Agent:** `AssemblyAgent`
**Tool:** FFmpeg (via Python wrapper)
**Input:** `visual_plan.json` + Asset Paths
**Output:** `timeline.json` (EDL) -> `render/output.mp4`

## Agent Interfaces

All agents inherit from a base `BaseAgent` class:

```python
class BaseAgent:
    def run(self, context: dict) -> dict:
        """
        Takes the current episode context, performs work, 
        and returns the updated context.
        """
        pass
```

## Configuration

Configuration is strictly separated from code in `config/settings.yaml`. This allows swapping models (e.g., Gemini 1.0 to 1.5) without code changes.
