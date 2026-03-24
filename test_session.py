"""Quick test: verify Kling session is still valid"""
import os, time
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.join(os.path.dirname(__file__), "config", "kling_browser_profile")
DEBUG_DIR = os.path.join(os.path.dirname(__file__), "output", "debug")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=False,
        viewport={"width": 1280, "height": 900},
        locale="en-US",
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = browser.pages[0] if browser.pages else browser.new_page()
    page.goto("https://app.klingai.com/global/omni/new?model=video", wait_until="networkidle", timeout=30000)
    time.sleep(5)
    
    page.screenshot(path=os.path.join(DEBUG_DIR, "session_test.png"))
    
    gen_btns = page.query_selector_all("button:has-text('Generate')")
    visible_gen = [b for b in gen_btns if b.is_visible()]
    print(f"Generate buttons visible: {len(visible_gen)}")
    print(f"URL: {page.url}")
    
    # Check for prompt input
    inputs = page.query_selector_all("textarea, div[contenteditable='true'], div[role='textbox']")
    print(f"Input elements: {len(inputs)}")
    
    # Get inner text of bottom bar for settings info
    body_text = page.inner_text("body")
    lines = [l.strip() for l in body_text.split("\n") if l.strip()]
    for l in lines:
        if any(k in l.lower() for k in ["video", "1080", "audio", "generate", "shot", "duration"]):
            print(f"  UI text: {l[:80]}")
    
    browser.close()
    print("Session test complete!")
