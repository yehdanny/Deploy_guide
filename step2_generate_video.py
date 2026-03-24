"""
Step 2: Generate video segments using Kling AI Web (browser automation)
Uses persistent browser session at app.klingai.com
Generates 3 x 5-second clips, downloads them, concatenates into 15-second short.
"""
import json
import os
import sys
import time
import re
import subprocess
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(PROJECT_DIR, "config")
PROFILE_DIR = os.path.join(CONFIG_DIR, "kling_browser_profile")
DEBUG_DIR = os.path.join(PROJECT_DIR, "output", "debug")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

KLING_CREATE_URL = "https://app.klingai.com/global/omni/new?model=video"


def configure_settings(page):
    """Configure video settings: try to use cheaper model, set 9:16, 5s, disable Native Audio."""
    time.sleep(2)
    
    # Click on model dropdown (VIDEO 3.0 Omni) to see if we can change it
    try:
        model_btn = page.query_selector("button:has-text('VIDEO 3'), span:has-text('VIDEO 3')")
        if model_btn and model_btn.is_visible():
            model_btn.click()
            time.sleep(1)
            page.screenshot(path=os.path.join(DEBUG_DIR, "model_dropdown.png"))
            
            # Look for cheaper model options (V1.0, V1.5, V2.0 etc)
            cheaper_models = ["VIDEO 1.0", "VIDEO 1.5", "VIDEO 2.0", "V1.0", "V1.5", "V2.0"]
            found_cheaper = False
            for model_name in cheaper_models:
                try:
                    opt = page.query_selector(f"text='{model_name}'")
                    if opt and opt.is_visible():
                        opt.click()
                        print(f"   ✅ Switched to {model_name} (cheaper)")
                        found_cheaper = True
                        time.sleep(1)
                        break
                except:
                    continue
            
            if not found_cheaper:
                # Close dropdown by pressing Escape
                page.keyboard.press("Escape")
                print("   ⚠️ Could not find cheaper model, using VIDEO 3.0 Omni")
    except Exception as e:
        print(f"   ⚠️ Model selection: {e}")
    
    # Try to set 9:16 aspect ratio
    try:
        res_btn = page.query_selector("button:has-text('1080'), span:has-text('1080')")
        if res_btn and res_btn.is_visible():
            res_btn.click()
            time.sleep(1)
            page.screenshot(path=os.path.join(DEBUG_DIR, "resolution_dropdown.png"))
            
            # Look for 9:16 option
            ratio_opt = page.query_selector("text='9:16'")
            if ratio_opt and ratio_opt.is_visible():
                ratio_opt.click()
                print("   ✅ Set 9:16 aspect ratio")
                time.sleep(1)
            else:
                page.keyboard.press("Escape")
    except Exception as e:
        print(f"   ⚠️ Ratio selection: {e}")
    
    # Try to disable Native Audio to save credits
    try:
        audio_btn = page.query_selector("button:has-text('Native Audio'), span:has-text('Native Audio')")
        if audio_btn and audio_btn.is_visible():
            # Check if it's enabled (has checkmark)
            parent = audio_btn
            text = parent.text_content()
            if "✓" in text or "✔" in text:
                audio_btn.click()
                print("   ✅ Disabled Native Audio (saves credits)")
                time.sleep(1)
    except Exception as e:
        print(f"   ⚠️ Audio toggle: {e}")
    
    # Try to disable Multi-Shot
    try:
        ms_btn = page.query_selector("button:has-text('Multi-Shot'), span:has-text('Multi-Shot')")
        if ms_btn and ms_btn.is_visible():
            text = ms_btn.text_content()
            if "✓" in text or "✔" in text:
                ms_btn.click()
                print("   ✅ Disabled Multi-Shot")
                time.sleep(1)
    except Exception as e:
        print(f"   ⚠️ Multi-Shot toggle: {e}")
    
    page.screenshot(path=os.path.join(DEBUG_DIR, "settings_configured.png"))


def generate_single_video(page, prompt, segment_num, total):
    """Generate a single video clip via Kling web UI."""
    print(f"\n{'='*50}")
    print(f"🎥 Segment {segment_num}/{total}")
    print(f"   Prompt: {prompt[:80]}...")
    print(f"{'='*50}")
    
    # Navigate to creation page
    page.goto(KLING_CREATE_URL, wait_until="networkidle", timeout=30000)
    time.sleep(3)
    
    # Find prompt input
    input_elem = page.query_selector("textarea, div[contenteditable='true'], div[role='textbox']")
    if not input_elem:
        page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{segment_num}_no_input.png"))
        raise Exception("Could not find prompt input field")
    
    # Clear and fill prompt
    input_elem.click()
    time.sleep(0.3)
    
    # Select all + delete to clear
    page.keyboard.press("Control+a")
    time.sleep(0.1)
    page.keyboard.press("Backspace")
    time.sleep(0.2)
    
    # Type the prompt
    input_elem.type(prompt, delay=10)
    time.sleep(0.5)
    
    page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{segment_num}_prompt_filled.png"))
    
    # Configure settings on first segment
    if segment_num == 1:
        print("   ⚙️ Configuring video settings...")
        configure_settings(page)
    
    # Click Generate
    gen_btn = page.query_selector("button:has-text('Generate')")
    if not gen_btn or not gen_btn.is_visible():
        page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{segment_num}_no_gen_btn.png"))
        raise Exception("Generate button not found")
    
    gen_btn.click()
    print("   ✅ Generate clicked!")
    time.sleep(3)
    
    page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{segment_num}_after_generate.png"))
    
    # Wait for video to complete
    print("   ⏳ Waiting for video generation (this takes 2-5 minutes)...")
    max_wait = 600  # 10 minutes max
    poll_interval = 15
    elapsed = 0
    
    while elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval
        
        # Look for video elements
        videos = page.query_selector_all("video")
        for v in videos:
            src = v.get_attribute("src")
            if src and src.startswith("http") and ("kling" in src or "cdn" in src or "video" in src.lower()):
                print(f"   ✅ Video found! ({elapsed}s)")
                page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{segment_num}_video_found.png"))
                return src
            # Check <source> children
            sources = v.query_selector_all("source")
            for s in sources:
                src = s.get_attribute("src")
                if src and src.startswith("http"):
                    print(f"   ✅ Video found via source! ({elapsed}s)")
                    return src
        
        # Check for download button/link
        dl_elements = page.query_selector_all("[class*='download'], button:has-text('Download'), a[download]")
        for dl in dl_elements:
            if dl.is_visible():
                print(f"   ✅ Download available! ({elapsed}s)")
                # Try to extract video URL from network or click download
                videos = page.query_selector_all("video")
                for v in videos:
                    src = v.get_attribute("src")
                    if src and src.startswith("http"):
                        return src
                
                # Click download as last resort
                try:
                    with page.expect_download(timeout=30000) as dl_info:
                        dl.click()
                    download = dl_info.value
                    return download
                except:
                    pass
        
        # Check for completion text
        body_text = page.inner_text("body")
        if "generation complete" in body_text.lower() or "video ready" in body_text.lower():
            print(f"   ✅ Completion text detected ({elapsed}s)")
            time.sleep(3)
            videos = page.query_selector_all("video")
            for v in videos:
                src = v.get_attribute("src")
                if src and src.startswith("http"):
                    return src
        
        # Check for errors
        if "insufficient" in body_text.lower() or "not enough" in body_text.lower():
            raise Exception("Insufficient credits!")
        
        if elapsed % 60 == 0:
            page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{segment_num}_wait_{elapsed}s.png"))
        
        print(f"   ⏳ Still generating... ({elapsed}s)")
    
    page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{segment_num}_timeout.png"))
    raise TimeoutError(f"Video generation timed out after {max_wait}s")


def download_video(source, output_path):
    """Download video from URL or Playwright Download object."""
    if isinstance(source, str):
        print(f"   📥 Downloading video...")
        resp = requests.get(source, stream=True, timeout=120)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        print(f"   📥 Saving download...")
        source.save_as(output_path)
    
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"   ✅ Saved: {output_path} ({size_mb:.1f} MB)")


def concat_videos(segment_files, output_file):
    """Concatenate video segments with ffmpeg."""
    list_file = output_file.replace(".mp4", "_list.txt")
    with open(list_file, "w") as f:
        for seg in segment_files:
            f.write(f"file '{os.path.abspath(seg)}'\n")
    
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
               "-c:v", "libx264", "-preset", "fast", "-crf", "23",
               "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", output_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"ffmpeg error: {result.stderr}")
    
    os.remove(list_file)
    print(f"✅ Concatenated: {output_file}")


def main(job_dir):
    os.makedirs(DEBUG_DIR, exist_ok=True)
    
    job_file = os.path.join(job_dir, "job.json")
    with open(job_file, "r", encoding="utf-8") as f:
        job = json.load(f)
    
    if job["status"] not in ("script_generated", "video_failed"):
        print(f"⚠️ Job status is '{job['status']}', skipping")
        return
    
    prompts = job["prompts"]
    segment_files = []
    
    print("=" * 60)
    print(f"🎬 {job['topic']['species_a']} vs {job['topic']['species_b']}")
    print(f"   Segments: {len(prompts)} x 5s")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 900},
            locale="en-US",
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Verify login
        page.goto(KLING_CREATE_URL, wait_until="networkidle", timeout=30000)
        time.sleep(3)
        
        gen_btn = page.query_selector("button:has-text('Generate')")
        if not gen_btn or not gen_btn.is_visible():
            print("❌ Not logged in! Please run: python kling_login.py")
            browser.close()
            return
        
        print("✅ Logged in!")
        
        for i, prompt in enumerate(prompts):
            try:
                video_src = generate_single_video(page, prompt, i + 1, len(prompts))
                
                seg_path = os.path.join(job_dir, f"segment_{i+1}.mp4")
                download_video(video_src, seg_path)
                segment_files.append(seg_path)
                
                if i < len(prompts) - 1:
                    print("   💤 Waiting 10s before next segment...")
                    time.sleep(10)
                    
            except Exception as e:
                print(f"   ❌ Segment {i+1} failed: {e}")
                page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{i+1}_error.png"))
                job["status"] = "video_failed"
                job["error"] = str(e)
                job["segment_files"] = segment_files
                with open(job_file, "w", encoding="utf-8") as f:
                    json.dump(job, f, ensure_ascii=False, indent=2)
                browser.close()
                return
        
        browser.close()
    
    # Concatenate if all segments done
    if len(segment_files) == len(prompts):
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            final_video = os.path.join(job_dir, "final_short.mp4")
            concat_videos(segment_files, final_video)
            job["video_file"] = final_video
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("⚠️ ffmpeg not found - segments saved but not concatenated")
            print("   Install: winget install ffmpeg")
            job["video_file"] = segment_files[0]
        
        job["status"] = "video_generated"
        job["segment_files"] = segment_files
        print(f"\n🎉 All {len(prompts)} segments generated!")
    else:
        job["status"] = "video_failed"
        job["segment_files"] = segment_files
    
    with open(job_file, "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python step2_generate_video.py <job_dir>")
        sys.exit(1)
    main(sys.argv[1])
