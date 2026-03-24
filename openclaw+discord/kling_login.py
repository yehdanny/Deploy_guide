"""
Kling AI - Login + save session
Opens browser at app.klingai.com for login.
"""
import os
import time
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.join(os.path.dirname(__file__), "config", "kling_browser_profile")
DEBUG_DIR = os.path.join(os.path.dirname(__file__), "output", "debug")

def main():
    os.makedirs(DEBUG_DIR, exist_ok=True)
    os.makedirs(PROFILE_DIR, exist_ok=True)
    
    print("🔐 Opening Kling AI for login...")
    print("   Please log in manually in the browser window.")
    print("   DO NOT close the browser - it will auto-close after login is verified.\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 900},
            locale="en-US",
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        # Use the CORRECT domain: app.klingai.com
        page.goto("https://app.klingai.com/global/omni/new?model=video", wait_until="networkidle", timeout=30000)
        
        print("✅ Browser opened. Please log in now.")
        print("   Waiting for login (up to 5 minutes)...\n")
        
        logged_in = False
        for i in range(60):
            time.sleep(5)
            
            url = page.url
            
            # If we're on the omni page and can see the Generate button, we're logged in
            if "omni" in url or "app.klingai.com" in url:
                gen_btns = page.query_selector_all("button:has-text('Generate')")
                if gen_btns:
                    for btn in gen_btns:
                        if btn.is_visible():
                            logged_in = True
                            print("✅ Login detected! (Generate button visible)")
                            break
                if logged_in:
                    break
                
                # Also check for prompt input area
                textareas = page.query_selector_all("textarea, div[contenteditable='true'], div[role='textbox']")
                if textareas:
                    logged_in = True
                    print("✅ Login detected! (prompt input found)")
                    break
            
            if i % 6 == 0 and i > 0:
                print(f"   Still waiting... ({i*5}s)")
        
        if logged_in:
            # Save screenshot to verify
            page.screenshot(path=os.path.join(DEBUG_DIR, "login_verified.png"))
            
            # Get cookies count
            cookies = browser.cookies()
            kling_cookies = [c for c in cookies if 'kling' in c.get('domain', '').lower()]
            print(f"   Kling cookies: {len(kling_cookies)}")
            
            # Wait a moment to make sure everything is saved
            time.sleep(3)
            
            print("\n✅ Session saved! Closing browser...")
        else:
            print("\n⚠️ Login timeout. Please try again.")
        
        browser.close()
    
    if logged_in:
        print("🎉 Done! You can now run the pipeline.")
    else:
        print("❌ Login was not detected. Please try again.")

if __name__ == "__main__":
    main()
