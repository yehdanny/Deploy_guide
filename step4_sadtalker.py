"""
Step 4: Generate talking head videos using SadTalker.
Each speaker's audio is synced with their portrait image.
"""
import subprocess
import sys
import json
from pathlib import Path
from config import OUTPUT_DIR, SADTALKER_DIR, SPEAKER_A_IMAGE, SPEAKER_B_IMAGE


def setup_sadtalker():
    """Clone and setup SadTalker if not present."""
    if not SADTALKER_DIR.exists():
        print("📦 Cloning SadTalker...")
        subprocess.run([
            "git", "clone", "--depth", "1",
            "https://github.com/OpenTalker/SadTalker.git",
            str(SADTALKER_DIR)
        ], check=True)
        
        print("📦 Installing SadTalker dependencies...")
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "-r", str(SADTALKER_DIR / "requirements.txt")
        ], check=True)
        
        print("✅ SadTalker setup complete")
    else:
        print("✅ SadTalker already installed")


def generate_talking_head(
    image_path: Path,
    audio_path: Path,
    output_path: Path,
    speaker_name: str = "Speaker"
):
    """
    Run SadTalker to generate a talking head video.
    
    Args:
        image_path: Path to the speaker's portrait image
        audio_path: Path to the speaker's audio track
        output_path: Path to save the output video
        speaker_name: Name for logging
    """
    print(f"🎭 Generating talking head for {speaker_name}...")
    print(f"   Image: {image_path}")
    print(f"   Audio: {audio_path}")
    
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return None
    
    if not audio_path.exists():
        print(f"❌ Audio not found: {audio_path}")
        return None
    
    result_dir = OUTPUT_DIR / "sadtalker_results"
    result_dir.mkdir(exist_ok=True)
    
    # Run SadTalker inference
    cmd = [
        sys.executable,
        str(SADTALKER_DIR / "inference.py"),
        "--driven_audio", str(audio_path),
        "--source_image", str(image_path),
        "--result_dir", str(result_dir),
        "--still",                    # Less head movement, more stable
        "--preprocess", "crop",       # Crop face from image
        "--enhancer", "gfpgan",       # Face enhancement
        "--size", "512",              # Output size
        "--expression_scale", "1.2",  # Slightly more expressive
        "--pose_style", "0",          # Neutral pose
    ]
    
    print(f"   Running SadTalker...")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(SADTALKER_DIR),
        timeout=600,  # 10 min timeout
    )
    
    if result.returncode != 0:
        print(f"❌ SadTalker failed for {speaker_name}")
        print(f"   stderr: {result.stderr[-500:]}")
        return None
    
    # Find the output video (SadTalker saves with timestamp)
    result_videos = sorted(result_dir.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not result_videos:
        print(f"❌ No output video found for {speaker_name}")
        return None
    
    latest = result_videos[0]
    
    # Move to desired output path
    import shutil
    shutil.move(str(latest), str(output_path))
    
    print(f"✅ {speaker_name} video: {output_path}")
    return output_path


def main():
    setup_sadtalker()
    
    # Check for speaker images
    if not SPEAKER_A_IMAGE.exists() or not SPEAKER_B_IMAGE.exists():
        print("⚠️ Speaker images not found!")
        print(f"   Please place images at:")
        print(f"   Speaker A: {SPEAKER_A_IMAGE}")
        print(f"   Speaker B: {SPEAKER_B_IMAGE}")
        print(f"   (Use realistic portrait photos, face clearly visible)")
        return
    
    # Generate for Speaker A
    video_a = generate_talking_head(
        image_path=SPEAKER_A_IMAGE,
        audio_path=OUTPUT_DIR / "speaker_a.wav",
        output_path=OUTPUT_DIR / "talker_a.mp4",
        speaker_name="Speaker A"
    )
    
    # Generate for Speaker B
    video_b = generate_talking_head(
        image_path=SPEAKER_B_IMAGE,
        audio_path=OUTPUT_DIR / "speaker_b.wav",
        output_path=OUTPUT_DIR / "talker_b.mp4",
        speaker_name="Speaker B"
    )
    
    if video_a and video_b:
        print("\n🎉 Both talking head videos generated!")
    else:
        print("\n⚠️ Some videos failed to generate")


if __name__ == "__main__":
    main()
