"""
All-in-one: Login to Kling + Generate videos in a single browser session.
No need to save/restore login - everything runs in one go.
"""
import json
import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

PROJECT_DIR = os.path.dirname(__file__)
CONFIG_DIR = os.path.join(PROJECT_DIR, "config")
PROFILE_DIR = os.path.join(CONFIG_DIR, "kling_browser_profile")
DEBUG_DIR = os.path.join(PROJECT_DIR, "output", "debug")

def wait_for_login(page):
    """Wait for user to log in on Kling."""
    print("\n🔐 Please log in to Kling AI in the browser window.")
    print("   Waiting for login (up to 5 minutes)...\n")
    
    for i in range(60):
        time.sleep(5)
        
        # Try navigating to creation page to check if logged in
        if i == 0 or (i % 12 == 0 and i > 0):
            page.goto("https://klingai.com/global/videos/text-to-video", wait_until="networkidle", timeout=30000)
            time.sleep(3)
        
        # Check if we're on the creation page (not redirected back to home)
        url = page.url
        if "text-to-video" in url or "creative-studio" in url:
            # Check for prompt input
            textareas = page.query_selector_all("textarea")
            editables = page.query_selector_all("[contenteditable='true']")
            if textareas or editables:
                print("✅ Logged in and on creation page!")
                return True
        
        # Check for any generation-related elements
        try:
            gen_elements = page.query_selector_all("[class*='generate'], [class*='Generate'], [class*='creation'], [class*='Creation']")
            if gen_elements:
                print("✅ Found creation elements - logged in!")
                return True
        except:
            pass
        
        if i % 6 == 0 and i > 0:
            print(f"   Still waiting for login... ({i*5}s)")
            page.screenshot(path=os.path.join(DEBUG_DIR, f"login_wait_{i*5}s.png"))
    
    return False

def find_prompt_input(page):
    """Find the prompt input field on Kling's creation page."""
    # Try various selectors
    selectors = [
        "textarea",
        "div[contenteditable='true']",
        "[class*='prompt'] textarea",
        "[class*='prompt'] div[contenteditable]",
        "[class*='input'] textarea",
        "[class*='editor'] textarea",
        "[class*='editor'] div[contenteditable]",
        "[class*='text-area'] textarea",
        "[class*='textarea']",
        "div[class*='ql-editor']",  # Quill editor
        "div[role='textbox']",
    ]
    
    for sel in selectors:
        try:
            elem = page.wait_for_selector(sel, timeout=3000)
            if elem and elem.is_visible():
                return elem, sel
        except:
            continue
    
    return None, None

def set_video_settings(page):
    """Try to set 9:16 ratio and 5s duration."""
    # Look for ratio selector
    try:
        ratio_options = page.query_selector_all("text=9:16, [data-value='9:16'], span:has-text('9:16')")
        for opt in ratio_options:
            if opt.is_visible():
                opt.click()
                print("   ✅ Set 9:16 ratio")
                time.sleep(1)
                break
    except:
        print("   ⚠️ Could not set ratio")
    
    # Look for 5s duration
    try:
        dur_options = page.query_selector_all("text=5s, [data-value='5'], span:has-text('5s'), button:has-text('5s')")
        for opt in dur_options:
            if opt.is_visible():
                opt.click()
                print("   ✅ Set 5s duration")
                time.sleep(1)
                break
    except:
        print("   ⚠️ Could not set duration")

def click_generate(page):
    """Find and click the generate button."""
    gen_selectors = [
        "button:has-text('Generate')",
        "button:has-text('Create')",
        "button:has-text('Start')",
        "button:has-text('Submit')",
        "[class*='generate'] button",
        "[class*='submit'] button",
        "button[class*='generate']",
        "button[class*='create']",
        "button[class*='primary']:visible",
    ]
    
    for sel in gen_selectors:
        try:
            btn = page.wait_for_selector(sel, timeout=3000)
            if btn and btn.is_visible():
                btn.click()
                print(f"   ✅ Generate clicked")
                return True
        except:
            continue
    
    return False

def wait_for_video(page, segment_num, max_wait=600):
    """Wait for video to finish generating and get download URL."""
    poll_interval = 15
    elapsed = 0
    
    while elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval
        
        page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{segment_num}_wait_{elapsed}s.png"))
        
        # Look for video element
        try:
            video_elems = page.query_selector_all("video")
            for v in video_elems:
                src = v.get_attribute("src")
                if src and src.startswith("http"):
                    print(f"   ✅ Video ready! ({elapsed}s)")
                    return src
                # Check source child elements
                sources = v.query_selector_all("source")
                for s in sources:
                    src = s.get_attribute("src")
                    if src and src.startswith("http"):
                        print(f"   ✅ Video ready! ({elapsed}s)")
                        return src
        except:
            pass
        
        # Look for download button
        try:
            dl_btns = page.query_selector_all("button:has-text('Download'), a:has-text('Download'), [class*='download']")
            for btn in dl_btns:
                if btn.is_visible():
                    print(f"   ✅ Download available! ({elapsed}s)")
                    # Try to get video URL first
                    video_elems = page.query_selector_all("video")
                    for v in video_elems:
                        src = v.get_attribute("src")
                        if src and src.startswith("http"):
                            return src
                    # Fallback: click download
                    try:
                        with page.expect_download(timeout=30000) as dl_info:
                            btn.click()
                        return dl_info.value
                    except:
                        pass
        except:
            pass
        
        # Check for completion indicators
        try:
            complete = page.query_selector_all("[class*='complete'], [class*='success'], [class*='finished'], [class*='done']")
            if complete:
                print(f"   ✅ Completion indicator found ({elapsed}s)")
                time.sleep(3)
                # Try to find video again
                video_elems = page.query_selector_all("video")
                for v in video_elems:
                    src = v.get_attribute("src")
                    if src and src.startswith("http"):
                        return src
        except:
            pass
        
        # Check for error
        try:
            errors = page.query_selector_all("[class*='error'], [class*='fail']")
            for err in errors:
                if err.is_visible():
                    text = err.text_content().strip()
                    if text and len(text) > 3:
                        raise Exception(f"Generation error: {text}")
        except Exception as e:
            if "Generation error" in str(e):
                raise
        
        print(f"   ⏳ Generating... ({elapsed}s / {max_wait}s)")
    
    raise TimeoutError(f"Video generation timed out after {max_wait}s")

def download_video_file(source, output_path):
    """Download video from URL or Playwright Download object."""
    if isinstance(source, str):
        import requests
        resp = requests.get(source, stream=True)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        source.save_as(output_path)
    
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"   ✅ Saved: {output_path} ({size_mb:.1f} MB)")

def concat_videos(segment_files, output_file):
    """Concatenate segments with ffmpeg."""
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
    print(f"✅ Final video: {output_file}")

def main(job_dir):
    os.makedirs(DEBUG_DIR, exist_ok=True)
    
    job_file = os.path.join(job_dir, "job.json")
    with open(job_file, "r", encoding="utf-8") as f:
        job = json.load(f)
    
    prompts = job["prompts"]
    segment_files = []
    
    print("=" * 60)
    print(f"🎬 Kling Video Generation: {job['topic']['species_a']} vs {job['topic']['species_b']}")
    print(f"   Segments: {len(prompts)}")
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
        
        # Navigate to creation page
        page.goto("https://klingai.com/global/videos/text-to-video", wait_until="networkidle", timeout=30000)
        time.sleep(3)
        page.screenshot(path=os.path.join(DEBUG_DIR, "initial_page.png"))
        
        # Check if logged in
        prompt_input, sel = find_prompt_input(page)
        if not prompt_input:
            # Need to log in first
            page.goto("https://klingai.com/global/", wait_until="networkidle", timeout=30000)
            if not wait_for_login(page):
                print("❌ Login failed or timed out.")
                browser.close()
                return
            
            # Navigate to creation page after login
            page.goto("https://klingai.com/global/videos/text-to-video", wait_until="networkidle", timeout=30000)
            time.sleep(5)
            page.screenshot(path=os.path.join(DEBUG_DIR, "after_login_creation.png"))
            
            prompt_input, sel = find_prompt_input(page)
            if not prompt_input:
                print("❌ Could not find prompt input even after login!")
                print("   Check debug screenshots in output/debug/")
                # Dump page info
                body = page.inner_text("body")
                with open(os.path.join(DEBUG_DIR, "creation_page_text.txt"), "w", encoding="utf-8") as f:
                    f.write(body)
                browser.close()
                return
        
        print(f"✅ Found prompt input (selector: {sel})")
        
        # Set video settings (do once)
        set_video_settings(page)
        
        # Generate each segment
        for i, prompt in enumerate(prompts):
            print(f"\n{'='*60}")
            print(f"🎥 Segment {i+1}/{len(prompts)}")
            print(f"   Prompt: {prompt[:80]}...")
            print(f"{'='*60}")
            
            if i > 0:
                # Navigate back to creation page for next segment
                page.goto("https://klingai.com/global/videos/text-to-video", wait_until="networkidle", timeout=30000)
                time.sleep(3)
                prompt_input, sel = find_prompt_input(page)
                if not prompt_input:
                    print(f"   ❌ Could not find prompt input for segment {i+1}")
                    break
            
            # Fill prompt
            prompt_input.click()
            time.sleep(0.3)
            prompt_input.fill("")
            time.sleep(0.2)
            prompt_input.fill(prompt)
            time.sleep(0.5)
            
            page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{i+1}_prompt_filled.png"))
            
            # Click generate
            if not click_generate(page):
                print(f"   ❌ Could not click Generate for segment {i+1}")
                page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{i+1}_gen_fail.png"))
                break
            
            page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{i+1}_generating.png"))
            
            # Wait for video
            try:
                print("   ⏳ Waiting for video generation...")
                video_src = wait_for_video(page, i + 1)
                
                seg_path = os.path.join(job_dir, f"segment_{i+1}.mp4")
                download_video_file(video_src, seg_path)
                segment_files.append(seg_path)
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                page.screenshot(path=os.path.join(DEBUG_DIR, f"seg{i+1}_error.png"))
                break
            
            # Wait between segments
            if i < len(prompts) - 1:
                print("   💤 Waiting 10s before next segment...")
                time.sleep(10)
        
        browser.close()
    
    # Update job status
    if len(segment_files) == len(prompts):
        # Try concatenation if ffmpeg available
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            final_video = os.path.join(job_dir, "final_short.mp4")
            concat_videos(segment_files, final_video)
            job["video_file"] = final_video
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("\n⚠️ ffmpeg not found, skipping concatenation")
            job["video_file"] = segment_files[0]  # Use first segment as placeholder
        
        job["status"] = "video_generated"
        job["segment_files"] = segment_files
        print(f"\n🎉 All {len(prompts)} segments generated!")
    else:
        job["status"] = "video_failed"
        job["error"] = f"Only {len(segment_files)}/{len(prompts)} segments completed"
        job["segment_files"] = segment_files
        print(f"\n❌ Only {len(segment_files)}/{len(prompts)} segments completed")
    
    with open(job_file, "w", encoding="utf-8") as f:
        json.dump(job, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_kling_session.py <job_dir>")
        sys.exit(1)
    main(sys.argv[1])
