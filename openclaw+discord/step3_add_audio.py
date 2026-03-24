"""
Step 3: Add animal sounds + ambient audio to the video
Uses freesound.org API or bundled sound effects
"""
import json
import os
import sys
import subprocess
import random

# Sound effect mappings (free sound effect search terms)
ANIMAL_SOUNDS = {
    "Lion": "lion roar growl",
    "Tiger": "tiger roar growl",
    "Leopard": "leopard growl snarl",
    "Snow Leopard": "leopard growl",
    "Cheetah": "cheetah chirp growl",
    "Hyena": "hyena laugh howl",
    "Wolf": "wolf howl growl",
    "Wild Dog Pack": "wild dog bark",
    "Bear": "bear roar growl",
    "Grizzly Bear": "bear roar growl",
    "Polar Bear": "polar bear growl",
    "Crocodile": "crocodile hiss snap",
    "Alligator": "alligator hiss",
    "Hippo": "hippo grunt roar",
    "Elephant": "elephant trumpet roar",
    "Rhino": "rhino snort charge",
    "Eagle": "eagle screech",
    "Harpy Eagle": "eagle screech",
    "Peregrine Falcon": "falcon screech",
    "Secretary Bird": "bird screech",
    "Osprey": "osprey call",
    "Cassowary": "cassowary boom",
    "Snake": "snake hiss rattle",
    "Cobra": "cobra hiss",
    "King Cobra": "cobra hiss",
    "Puff Adder": "snake hiss",
    "Python": "python hiss",
    "Anaconda": "snake hiss",
    "Shark": "underwater splash",
    "Great White Shark": "underwater splash",
    "Orca": "orca whale call",
    "Octopus": "underwater ambient",
    "Gorilla": "gorilla chest beat roar",
    "Baboon": "baboon screech bark",
    "Komodo Dragon": "lizard hiss",
    "Jaguar": "jaguar roar growl",
    "Wolverine": "wolverine snarl",
    "Mongoose": "mongoose chatter",
    "Honey Badger": "badger snarl growl",
    "Wild Boar": "boar squeal grunt",
    "Warthog": "warthog squeal",
    "Walrus": "walrus bellow",
    "Cape Buffalo": "buffalo snort",
    "Wild Buffalo": "buffalo snort",
    "Wildebeest": "wildebeest call",
    "Bharal": "goat bleat",
    "Moose": "moose call",
    "Caiman": "caiman hiss",
    "Giant Otter": "otter squeal",
    "Dingo": "dingo howl",
    "Sloth": "ambient forest",
    "Mantis Shrimp": "underwater snap",
    "Crab": "underwater ambient",
    "Tarantula Hawk Wasp": "wasp buzz",
    "Tarantula": "ambient desert",
    "Pigeon": "pigeon coo wings",
    "Large Fish": "fish splash water",
}

ENVIRONMENT_SOUNDS = {
    "African savannah": "savannah wind grassland birds",
    "African river": "river water flowing birds",
    "Rocky cliff": "wind cliff mountain",
    "Northern forest": "forest wind birds",
    "Asian jungle": "jungle birds insects",
    "Deep ocean": "deep ocean underwater ambient",
    "African bush": "bush savannah wind insects",
    "Indonesian island": "tropical island birds insects",
    "African woodland": "woodland birds wind",
    "Amazon rainforest": "rainforest jungle birds rain",
    "Arctic ice": "arctic wind ice cracking",
    "African grassland": "grassland wind insects",
    "Open ocean": "ocean waves wind",
    "Congo rainforest": "rainforest birds insects rain",
    "Indian grassland": "grassland wind birds india",
    "Coral reef": "underwater reef bubbles",
    "South American canopy": "rainforest canopy birds",
    "East African plains": "savannah wind grassland",
    "Florida Everglades": "swamp water birds insects",
    "Taiga forest": "forest wind cold",
    "Canadian wilderness": "wilderness wind forest creek",
    "Lake shore": "lake water birds wind",
    "Desert": "desert wind sand",
    "Serengeti": "savannah wind grassland birds",
    "Himalayan cliff": "mountain wind cold",
    "Australian rainforest": "rainforest birds insects",
    "Amazon river": "river water jungle birds",
    "Urban skyline": "city wind building",
}

def check_ffmpeg():
    """Verify ffmpeg is available."""
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def generate_synthetic_audio(output_path, duration=15):
    """Generate a simple ambient audio track using ffmpeg (no external API needed)."""
    # Generate pink noise as ambient background
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"anoisesrc=d={duration}:c=pink:a=0.02",
        "-af", "lowpass=f=2000,highpass=f=100",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"⚠️ Audio generation warning: {result.stderr[:200]}")
    return os.path.exists(output_path)

def add_audio_to_video(video_path, audio_path, output_path):
    """Merge audio track with video."""
    # If video already has audio, mix them
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-filter_complex",
        "[0:a]volume=1.0[va];[1:a]volume=0.3[aa];[va][aa]amix=inputs=2:duration=shortest[out]",
        "-map", "0:v", "-map", "[out]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        # Video might not have audio track, just add new audio
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"ffmpeg error: {result.stderr}")
    
    print(f"✅ Audio added: {output_path}")

def main(job_dir):
    job_file = os.path.join(job_dir, "job.json")
    with open(job_file, "r", encoding="utf-8") as f:
        job = json.load(f)
    
    if job["status"] != "video_generated":
        print(f"⚠️ Job status is '{job['status']}', expected 'video_generated'")
        if job["status"] == "audio_added":
            print("   Audio already added, skipping.")
            return
        return
    
    if not check_ffmpeg():
        print("❌ ffmpeg not found! Please install ffmpeg.")
        print("   Windows: winget install ffmpeg")
        print("   Or download from: https://ffmpeg.org/download.html")
        sys.exit(1)
    
    video_file = job.get("video_file")
    if not video_file or not os.path.exists(video_file):
        print(f"❌ Video file not found: {video_file}")
        return
    
    # Get video duration
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", video_file
    ]
    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
    except:
        duration = 15  # default
    
    print(f"🔊 Adding audio to video ({duration:.1f}s)...")
    
    # Generate ambient audio
    audio_file = os.path.join(job_dir, "ambient_audio.aac")
    print("   🎵 Generating ambient background audio...")
    generate_synthetic_audio(audio_file, duration=int(duration) + 1)
    
    # Merge audio with video
    output_file = os.path.join(job_dir, "final_short_audio.mp4")
    add_audio_to_video(video_file, audio_file, output_file)
    
    job["status"] = "audio_added"
    job["final_video"] = output_file
    with open(job_file, "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Audio processing complete!")
    print(f"📁 Final video with audio: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python step3_add_audio.py <job_dir>")
        sys.exit(1)
    main(sys.argv[1])
