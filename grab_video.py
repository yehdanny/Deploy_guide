"""Grab video from Kling - use API to get works list and download URL."""
import os, time, json, requests
from playwright.sync_api import sync_playwright

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(PROJECT_DIR, "config", "kling_browser_profile")
DEBUG_DIR = os.path.join(PROJECT_DIR, "output", "debug")
JOB_DIR = os.path.join(PROJECT_DIR, "output", "20260323_164613_Mantis_Shrimp_vs_Crab")

os.makedirs(DEBUG_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=False,
        viewport={"width": 1280, "height": 900},
        locale="en-US",
        args=["--disable-blink-features=AutomationControlled"],
        accept_downloads=True
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    
    # Set up network interception to capture video URLs
    video_urls = []
    def capture_response(response):
        url = response.url
        ct = response.headers.get("content-type", "")
        if ("video" in ct or ".mp4" in url) and "upload-ylab" in url:
            video_urls.append(url)
            print(f"  🎯 Captured video URL: {url[:150]}")
        # Also capture API responses that might contain video download URLs
        if "api-app-global.klingai.com" in url and "works" in url:
            try:
                body = response.json()
                print(f"  📡 API works response: {json.dumps(body)[:300]}")
            except:
                pass
    
    page.on("response", capture_response)
    
    page.goto("https://app.klingai.com/global/omni/new?model=video", wait_until="load", timeout=60000)
    time.sleep(8)
    
    # Method 1: Try clicking the download icon via the interactive overlay
    print("=== Method 1: Click download via overlay ===")
    
    # The download dropdown exists but is hidden. Find the trigger.
    # From DOM: there are 'top-action' buttons near the video
    # Let me try clicking on the interactive overlay first to get controls
    overlay = page.query_selector("div[class*='kwai-player-video-interactive']")
    if overlay:
        print("  Found video overlay, clicking...")
        overlay.click(force=True)
        time.sleep(2)
    
    # Now try to find and click the download trigger
    # The download dropdown's trigger is likely one of the 'top-action' buttons
    top_actions = page.query_selector_all(".top-action")
    print(f"  Top actions: {len(top_actions)}")
    
    for i, action in enumerate(top_actions):
        try:
            action.hover(force=True, timeout=5000)
            time.sleep(0.5)
            # Check tooltip
            tooltips = page.query_selector_all("[role='tooltip'], .el-popper")
            for tt in tooltips:
                if tt.is_visible():
                    text = (tt.text_content() or "").strip()
                    print(f"    Action[{i}] tooltip: '{text}'")
                    if "download" in text.lower():
                        print("    ✅ Found download action!")
                        action.click(force=True)
                        time.sleep(2)
                        page.screenshot(path=os.path.join(DEBUG_DIR, "download_menu.png"))
                        
                        # Click MP4 option
                        mp4_opt = page.query_selector("text='MP4'")
                        if mp4_opt and mp4_opt.is_visible():
                            print("    Clicking MP4...")
                            with page.expect_download(timeout=60000) as dl_info:
                                mp4_opt.click()
                            download = dl_info.value
                            seg_path = os.path.join(JOB_DIR, "segment_1.mp4")
                            download.save_as(seg_path)
                            size_mb = os.path.getsize(seg_path) / (1024*1024)
                            print(f"    ✅ Downloaded: {seg_path} ({size_mb:.1f} MB)")
                            break
        except Exception as e:
            print(f"    Action[{i}] error: {str(e)[:80]}")
    
    # Method 2: Use the Kling internal API to get download URL  
    if not video_urls:
        print("\n=== Method 2: Use Kling API ===")
        
        # Get cookies for API call
        cookies = browser.cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies if 'kling' in c.get('domain', '')])
        
        # Try to get works list via page's fetch
        api_result = page.evaluate("""async () => {
            try {
                const resp = await fetch('https://api-app-global.klingai.com/api/user/works/personal/v2?pageNum=1&pageSize=5&type=video', {
                    credentials: 'include'
                });
                const data = await resp.json();
                return JSON.stringify(data);
            } catch(e) {
                return 'Error: ' + e.message;
            }
        }""")
        
        print(f"  API result: {api_result[:500]}")
        
        try:
            data = json.loads(api_result)
            if data.get("data") and data["data"].get("works"):
                works = data["data"]["works"]
                print(f"  Found {len(works)} works")
                if works:
                    latest = works[0]
                    print(f"  Latest work: {json.dumps(latest)[:300]}")
                    # Try to find download URL
                    video_url = latest.get("resource", {}).get("resource", "") or latest.get("videoUrl", "") or latest.get("url", "")
                    if not video_url:
                        # Search nested
                        for key in ["resource", "video", "result", "output"]:
                            if key in latest and isinstance(latest[key], dict):
                                for k2, v2 in latest[key].items():
                                    if isinstance(v2, str) and ("http" in v2 and ("video" in v2 or "mp4" in v2)):
                                        video_url = v2
                                        break
                            if video_url:
                                break
                    
                    if video_url:
                        print(f"  ✅ Video URL: {video_url[:150]}")
                        video_urls.append(video_url)
        except:
            pass
    
    # Method 3: Direct download from captured performance entry URL
    if not video_urls:
        print("\n=== Method 3: Try known CDN URL pattern ===")
        perf_urls = page.evaluate("""() => {
            return performance.getEntriesByType('resource')
                .filter(e => e.name.includes('upload-ylab') && e.name.includes('video'))
                .map(e => e.name);
        }""")
        video_urls.extend(perf_urls)
        print(f"  Found {len(perf_urls)} CDN URLs")
        for u in perf_urls:
            print(f"  {u[:150]}")
    
    # Download the video if we found a URL
    if video_urls:
        url = video_urls[0]
        print(f"\n✅ Downloading from: {url[:150]}")
        seg_path = os.path.join(JOB_DIR, "segment_1.mp4")
        
        # Use page context to download (keeps auth cookies)
        dl_result = page.evaluate("""async (url) => {
            try {
                const resp = await fetch(url, {credentials: 'include'});
                const blob = await resp.blob();
                return {size: blob.size, type: blob.type, ok: resp.ok, status: resp.status};
            } catch(e) {
                return {error: e.message};
            }
        }""", url)
        print(f"  Fetch result: {dl_result}")
        
        # Try direct download with requests
        try:
            resp = requests.get(url, stream=True, timeout=120, headers={
                "Referer": "https://app.klingai.com/",
                "User-Agent": "Mozilla/5.0"
            })
            if resp.status_code == 200:
                with open(seg_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                size_mb = os.path.getsize(seg_path) / (1024*1024)
                print(f"  ✅ Downloaded: {seg_path} ({size_mb:.1f} MB)")
                
                # Update job
                job_file = os.path.join(JOB_DIR, "job.json")
                with open(job_file, "r", encoding="utf-8") as f:
                    job = json.load(f)
                job["status"] = "video_generated"
                job["video_file"] = seg_path
                job["segment_files"] = [seg_path]
                with open(job_file, "w", encoding="utf-8") as f:
                    json.dump(job, f, ensure_ascii=False, indent=2)
                print("  ✅ Job updated!")
            else:
                print(f"  ❌ HTTP {resp.status_code}")
        except Exception as e:
            print(f"  ❌ Download error: {e}")
    else:
        print("\n❌ No video URL found")
    
    page.screenshot(path=os.path.join(DEBUG_DIR, "grab3_final.png"))
    browser.close()
    print("\nDone!")
