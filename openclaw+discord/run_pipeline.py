"""
🎬 Animal Shorts Pipeline - One-Click Runner
Runs all 4 steps: Script → Video → Audio → Upload
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from step1_generate_script import main as generate_script
from step2_generate_video import main as generate_video
from step3_add_audio import main as add_audio
from step4_upload_youtube import main as upload_youtube

def run_pipeline(skip_upload=False):
    print("=" * 60)
    print("🎬 Animal Shorts Pipeline")
    print("=" * 60)
    
    # Step 1: Generate script
    print("\n" + "=" * 60)
    print("📝 Step 1: Generating script...")
    print("=" * 60)
    job_dir = generate_script()
    
    # Step 2: Generate video via Kling AI
    print("\n" + "=" * 60)
    print("🎥 Step 2: Generating video segments...")
    print("=" * 60)
    generate_video(job_dir)
    
    # Step 3: Add audio
    print("\n" + "=" * 60)
    print("🔊 Step 3: Adding audio...")
    print("=" * 60)
    add_audio(job_dir)
    
    # Step 4: Upload to YouTube
    if not skip_upload:
        print("\n" + "=" * 60)
        print("📤 Step 4: Uploading to YouTube...")
        print("=" * 60)
        upload_youtube(job_dir)
    else:
        print("\n⏭️ Skipping upload (--skip-upload flag)")
    
    print("\n" + "=" * 60)
    print("🎉 Pipeline complete!")
    print(f"📁 Job directory: {job_dir}")
    print("=" * 60)

if __name__ == "__main__":
    skip = "--skip-upload" in sys.argv
    run_pipeline(skip_upload=skip)
