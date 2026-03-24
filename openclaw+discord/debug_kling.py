"""Debug: check Kling page structure after login"""
import os
import time
from playwright.sync_api import sync_playwright

PROFILE_DIR = os.path.join(os.path.dirname(__file__), "config", "kling_browser_profile")
DEBUG_DIR = os.path.join(os.path.dirname(__file__), "output", "debug")

def main():
    os.makedirs(DEBUG_DIR, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            viewport={"width": 1280, "height": 900},
            locale="en-US"
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        
        # Go to video generation page
        print("Navigating to Kling...")
        page.goto("https://klingai.com/global/videos/text-to-video", wait_until="networkidle", timeout=30000)
        time.sleep(5)
        
        # Screenshot
        page.screenshot(path=os.path.join(DEBUG_DIR, "kling_page.png"), full_page=True)
        print(f"Screenshot saved to {DEBUG_DIR}/kling_page.png")
        
        # Get page URL (might have redirected)
        print(f"Current URL: {page.url}")
        
        # Get page title
        print(f"Page title: {page.title()}")
        
        # Look for key elements
        print("\n--- Looking for elements ---")
        
        # All textareas
        textareas = page.query_selector_all("textarea")
        print(f"Textareas found: {len(textareas)}")
        
        # All contenteditable
        editables = page.query_selector_all("[contenteditable='true']")
        print(f"Contenteditable elements: {len(editables)}")
        
        # All buttons
        buttons = page.query_selector_all("button")
        print(f"Buttons found: {len(buttons)}")
        for btn in buttons[:20]:
            text = btn.text_content().strip()[:50]
            if text:
                print(f"  Button: '{text}'")
        
        # Look for login indicators
        print("\n--- Login check ---")
        # Avatar/profile indicator
        avatars = page.query_selector_all("[class*='avatar'], [class*='profile'], [class*='user']")
        print(f"Avatar/profile elements: {len(avatars)}")
        
        # Login button
        login_btns = page.query_selector_all("button:has-text('Log in'), button:has-text('Sign in'), a:has-text('Log in'), a:has-text('Sign in')")
        print(f"Login buttons: {len(login_btns)}")
        
        # Dump all visible text for analysis
        body_text = page.inner_text("body")
        with open(os.path.join(DEBUG_DIR, "page_text.txt"), "w", encoding="utf-8") as f:
            f.write(body_text)
        print(f"\nFull page text saved to {DEBUG_DIR}/page_text.txt")
        
        # Get HTML of main content area
        html = page.content()
        with open(os.path.join(DEBUG_DIR, "page_html.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Full HTML saved to {DEBUG_DIR}/page_html.html")
        
        browser.close()
        print("\nDone!")

if __name__ == "__main__":
    main()
