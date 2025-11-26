import argparse
import json
import os
import subprocess
import sys

def render_video(episode_id, episodes_dir="episodes"):
    episode_path = os.path.join(episodes_dir, episode_id)
    timeline_path = os.path.join(episode_path, "timeline.json")
    output_path = os.path.join(episode_path, "final_video.mp4")
    
    if not os.path.exists(timeline_path):
        print(f"ERROR: Timeline not found at {timeline_path}")
        return

    with open(timeline_path, 'r') as f:
        timeline = json.load(f)
        
    print(f"Rendering {episode_id} to {output_path}...")
    
    # Build FFmpeg filter complex
    # This is a simplified renderer that concatenates visuals and mixes audio
    # A robust implementation would handle complex transitions and layers
    
    # 1. Generate a file list for visual concatenation
    # We'll assume a simple sequence of images for now
    
    video_tracks = timeline.get('tracks', {}).get('video', [])
    audio_tracks = timeline.get('tracks', {}).get('audio', [])
    
    if not video_tracks:
        print("ERROR: No video tracks found.")
        return

    # Create a temporary concat file for ffmpeg
    concat_list_path = os.path.join(episode_path, "video_concat.txt")
    with open(concat_list_path, 'w', encoding='utf-8') as f:
        for clip in video_tracks:
            image_path = clip.get('image_file')
            
            # Fix path logic: 
            # If path is absolute, use it.
            # If it exists relative to CWD, use it.
            # If not, try joining with episode_path.
            
            if not os.path.isabs(image_path):
                if os.path.exists(image_path):
                    pass # Use as is (relative to CWD)
                else:
                    joined_path = os.path.join(episode_path, image_path)
                    if os.path.exists(joined_path):
                        image_path = joined_path
                    else:
                        # Fallback: try to find it in assets/images assuming image_path is just filename
                        filename = os.path.basename(image_path)
                        assets_path = os.path.join(episode_path, "assets", "images", filename)
                        if os.path.exists(assets_path):
                             image_path = assets_path
            
            if not os.path.exists(image_path):
                print(f"WARNING: Image file not found: {image_path}")
            
            duration = clip.get('end_time_sec', 0) - clip.get('start_time_sec', 0)
            
            # FFmpeg concat format (use absolute paths)
            abs_path = os.path.abspath(image_path).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")
            f.write(f"duration {duration}\n")
            
        # Repeat last image to prevent cut-off
        last_clip = video_tracks[-1]
        last_path = last_clip.get('image_file')
        # Apply same logic for last clip
        if not os.path.isabs(last_path):
             if os.path.exists(last_path):
                 pass
             else:
                 last_path = os.path.join(episode_path, last_path)
                 
        abs_last_path = os.path.abspath(last_path).replace('\\', '/')
        f.write(f"file '{abs_last_path}'\n")

    # 2. Construct Audio Mix
    # For simplicity, we will concatenate audio chunks. 
    # A real timeline needs precise mixing at timestamps.
    # Here we assume audio chunks are sequential and roughly match video.
    
    audio_concat_path = os.path.join(episode_path, "audio_concat.txt")
    with open(audio_concat_path, 'w', encoding='utf-8') as f:
        for clip in audio_tracks:
            audio_path = clip.get('audio_file')
            
            if not os.path.isabs(audio_path):
                if os.path.exists(audio_path):
                    pass
                else:
                    joined_path = os.path.join(episode_path, audio_path)
                    if os.path.exists(joined_path):
                        audio_path = joined_path
                    else:
                         filename = os.path.basename(audio_path)
                         assets_path = os.path.join(episode_path, "assets", "audio", filename)
                         if os.path.exists(assets_path):
                             audio_path = assets_path

            if not os.path.exists(audio_path):
                print(f"WARNING: Audio file not found: {audio_path}")
                continue # Skip missing audio files

            # Use clean absolute paths with forward slashes
            abs_path = os.path.abspath(audio_path).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")

    # 3. Run FFmpeg
    # Command: ffmpeg -f concat -safe 0 -i video.txt -f concat -safe 0 -i audio.txt -c:v libx264 -c:a aac -pix_fmt yuv420p out.mp4
    
    cmd = [
        "ffmpeg",
        "-y", # Overwrite
        "-f", "concat", "-safe", "0", "-i", concat_list_path,
        "-f", "concat", "-safe", "0", "-i", audio_concat_path,
        "-c:v", "libx264", "-r", "30", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", # Stop when shortest stream ends
        output_path
    ]
    
    print(f"Running FFmpeg: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print("Render complete.")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed with audio: {e}")
        print("Retrying video-only render due to potential audio corruption/missing files...")
        
        # Remove audio inputs and mapping
        # Indexes in cmd: 
        # 0: ffmpeg, 1: -y, 2: -f, 3: concat, 4: -safe, 5: 0, 6: -i, 7: video_list
        # 8: -f, 9: concat, 10: -safe, 11: 0, 12: -i, 13: audio_list
        # We want to keep up to index 7, then skip 8-13, then keep the rest (-c:v ...)
        
        # Cleaner construction:
        cmd_video_only = [
            "ffmpeg",
            "-y",
            "-f", "concat", "-safe", "0", "-i", concat_list_path,
            "-c:v", "libx264", "-r", "30", "-pix_fmt", "yuv420p",
            # Remove audio codec args
            # "-c:a", "aac", "-b:a", "192k", 
            "-shortest",
            output_path
        ]
        
        try:
            subprocess.run(cmd_video_only, check=True)
            print("Video-only render complete (Audio omitted due to errors).")
        except subprocess.CalledProcessError as e2:
             print(f"FFmpeg video-only render also failed: {e2}")

    except FileNotFoundError:
        print("ERROR: FFmpeg not found in PATH.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episode_id", required=True)
    args = parser.parse_args()
    
    render_video(args.episode_id)
