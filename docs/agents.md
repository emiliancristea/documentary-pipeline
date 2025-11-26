# Script Writer Agent

The Script Writer Agent is the core narrative engine of the pipeline. It transforms a structured episode brief into a full documentary script.

## Configuration

- **Prompt File:** `prompts/script_writer_global.md`
- **Model:** Gemini 1.5 Pro (configured in `settings.yaml`)

## Series Logic

The agent modifies its output style and focus based on the `series` field in the episode brief. Supported series:

- **Origins & Reconstructions:** Focus on process, cause/effect, and plausible reconstruction.
- **Texts & Primary Sources:** Focus on specific documents, authorship, and context.
- **Artifacts & Archaeology:** Focus on physical evidence, excavation, and scientific method.
- **Power, Empires & Diplomacy:** Focus on statecraft, logistics, and political reality vs propaganda.
- **Ancient Science, Technology & Engineering:** Focus on mechanics, limitations, and practical application.
- **Economy, Everyday Life & Trade Routes:** Focus on common people, prices, and daily survival.
- **Method, Myths & Responsible Debunking:** Focus on historiography, evidence analysis, and correcting misconceptions.

## Output Format

The agent produces a Markdown file containing:

1.  **Episode Metadata:** Title, duration, audience level.
2.  **Segment Outline:** Timestamps and structure.
3.  **Full Voice-Over Script:** The narration text.
4.  **Visual Suggestions:** Detailed visual ideas for each segment.
5.  **Source Notes:** Hints for fact-checking and further research.

---

# Structure & Timing Agent

Refines the raw script into a machine-readable structure with precise timing.

- **Prompt:** `prompts/structure_timing_agent.md`
- **Input:** Brief + Script
- **Output:** `structure.json` (Segments, timing, visual slots)

# Image Prompt Agent

Translates visual suggestions into high-fidelity prompts for Google Imagen.

- **Prompt:** `prompts/image_prompt_agent.md`
- **Input:** `structure.json` + Script Visuals
- **Output:** `image_prompts.json` (Detailed prompts per slot)
- **Execution:** Calls `utils.google_api.generate_image` to create assets in `assets/images/`.

# Voice-Over Agent

Plans and orchestrates the Text-to-Speech generation.

- **Prompt:** `prompts/voice_over_agent.md`
- **Input:** Script + Structure
- **Output:** `tts_plan.json` + Audio Files in `assets/audio/`
- **Execution:** Calls `utils.google_api.synthesize_speech` using Gemini TTS.

# Video Assembly Agent

Combines all assets into a final timeline plan.

- **Prompt:** `prompts/video_assembly_agent.md`
- **Input:** Structure + Image Prompts + TTS Plan
- **Output:** `timeline.json` (EDL-like structure)

# QA / Consistency Agent

Reviews the generated content for historical accuracy and brand alignment.

- **Prompt:** `prompts/qa_agent.md`
- **Input:** Brief + Script + Structure
- **Output:** `qa_report.md`

# Video Renderer

A tool (`tools/render_video.py`) that executes the `timeline.json` plan.

- **Input:** `timeline.json`, `assets/images/`, `assets/audio/`
- **Output:** `final_video.mp4`
- **Engine:** FFmpeg (via subprocess)
