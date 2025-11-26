# KNOW: HISTORY - Automated Documentary Pipeline

**Project:** Automated YouTube Documentary Production  
**Channel:** KNOW: HISTORY (@KnowNowHistory)  
**Tech Stack:** Python, Google Vertex AI (Gemini, Imagen), Google Cloud TTS, FFmpeg

## Overview

This project contains a modular, agentic pipeline designed to go from a simple **Episode Brief** to a fully assembled video timeline (and rendered video). It strictly adheres to the "KNOW: HISTORY" brand guidelines: calm, intelligent, distinguishing consensus from speculation.

## Architecture

The system is orchestrated by `main.py`, which passes a state object (the `EpisodeContext`) through a series of specialized AI Agents.

### The Pipeline Steps:

1.  **Brief Normalization:** Validates and expands the user's input brief.
2.  **Script Writer (Gemini):** Writes a structured documentary script (Hook -> Act 1 -> Act 2 -> Act 3 -> Conclusion).
3.  **Structure & Timing:** Breaks the script into segments, estimates duration, and assigns visual intent.
4.  **Visual Director (Gemini):** Generates detailed image prompts for each segment.
5.  **Production (Imagen):** Generates high-fidelity assets for the visual prompts.
6.  **Narration (Google TTS):** Generates voice-over audio files.
7.  **Assembly:** Combines Audio, Images, and Timing into a `timeline.json` and renders the final video via FFmpeg.

## Directory Structure

- `agents/`: Python classes defining the logic for each step of the pipeline.
- `config/`: YAML configuration files for models, paths, and API settings.
- `prompts/`: Markdown files containing the system prompts for the AI agents.
- `episodes/`: Storage for episode data. Each episode gets its own folder (e.g., `episodes/001_roman_concrete/`).
- `utils/`: Helper functions for Google API interaction and file handling.
- `docs/`: Detailed architectural documentation.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Google Cloud Credentials:**
    - Ensure you have a Google Cloud Project with Vertex AI and Text-to-Speech APIs enabled.
    - Set your credentials:
      ```bash
      export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-service-account.json"
      ```
    - Update `config/settings.yaml` with your Project ID and Region.

3.  **FFmpeg:**
    - Ensure `ffmpeg` is installed and available in your system PATH.

## Real Asset Generation and Rendering

To run the pipeline with real Google AI models and generate a final video:

1.  **Requirements:**
    - Install the GenAI client: `pip install google-genai`
    - Ensure `ffmpeg` is in your system PATH.

2.  **Configuration (`config/settings.yaml`):**
    - **API Key:** Ensure `google.api_key` is set in `config/settings.yaml`.
    - **Runtime:** Set `runtime.mock_mode: false` to use real models.
    - **Models:** Verify model names (defaults are `gemini-2.0-flash-exp` for text/TTS and `imagen-3.0-generate-001` for images).

3.  **Run with Render:**
    ```bash
    python main.py --brief episodes/my_brief.yaml --name My_Episode --render
    ```

    This will:
    - Generate a script and structure.
    - Create real images using Imagen.
    - Synthesize real voice-over using Gemini TTS.
    - Assemble a final `.mp4` video in `episodes/My_Episode/final_video.mp4`.

## Usage

**1. Create a Brief:**
Copy `episodes/templates/brief_template.yaml` to a new file (e.g., `my_episode_brief.yaml`) and fill it out.

**2. Run the Pipeline (Dry Run):**
```bash
# Ensure runtime.mock_mode is true in settings.yaml
python main.py --brief my_episode_brief.yaml --name "The_Bronze_Age_Collapse"
```

**3. Run Production Build:**
See section above.

