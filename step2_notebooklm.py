"""
Step 2: NotebookLM Browser Automation
- Create notebook with article content
- Generate Traditional Chinese audio summary (short, dual-host podcast)
- Download the generated audio file
"""
import sys, io
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
if sys.stderr and hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright
from config import (
    NOTEBOOKLM_URL, NOTEBOOKLM_WAIT_SECONDS,
    COOKIES_DIR, OUTPUT_DIR
)


COOKIES_FILE = COOKIES_DIR / "notebooklm_cookies.json"


async def save_cookies(context):
    """Save browser cookies for reuse."""
    cookies = await context.cookies()
    import json
    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f)
    print("🍪 Cookies saved")


async def load_cookies(context):
    """Load saved cookies."""
    import json
    if COOKIES_FILE.exists():
        with open(COOKIES_FILE) as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        print("🍪 Cookies loaded")
        return True
    return False


async def manual_login():
    """Launch browser for manual Google login, save cookies."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto(NOTEBOOKLM_URL)
        
        print("=" * 60)
        print("🔑 Please log in to your Google account in the browser.")
        print("   After logging in and seeing NotebookLM, press Enter here.")
        print("=" * 60)
        input("Press Enter when done...")
        
        await save_cookies(context)
        await browser.close()
        print("✅ Login complete. Cookies saved.")


async def generate_podcast(article_title: str, article_content: str, output_path: Path):
    """
    Automate NotebookLM to generate a podcast from article content.
    
    Flow:
    1. Go to NotebookLM
    2. Create new notebook
    3. Paste article as source
    4. Go to Audio Overview
    5. Set language to Traditional Chinese, length to Short
    6. Generate and download
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headful for debugging
        context = await browser.new_context(
            accept_downloads=True,
            locale="zh-TW",
        )
        
        # Load cookies
        if not await load_cookies(context):
            print("❌ No cookies found. Run manual_login() first.")
            await browser.close()
            return None
        
        page = await context.new_page()
        
        # Set download path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. Navigate to NotebookLM
            print("📝 Opening NotebookLM...")
            await page.goto(NOTEBOOKLM_URL, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(3000)
            
            # 2. Create new notebook
            print("📓 Creating new notebook...")
            # Look for "New notebook" or "+" button
            new_btn = page.locator('button:has-text("New"), button:has-text("新增"), [aria-label*="new"], [aria-label*="新增"]').first
            await new_btn.click(timeout=10000)
            await page.wait_for_timeout(2000)
            
            # 3. Add source - paste text
            print("📋 Adding article as source...")
            # Look for "Paste text" or "Copy and paste text" option
            paste_btn = page.locator('button:has-text("Paste"), button:has-text("貼上"), button:has-text("Copy and paste"), [aria-label*="paste"]').first
            await paste_btn.click(timeout=10000)
            await page.wait_for_timeout(1000)
            
            # Find text area and paste content
            text_area = page.locator('textarea, [contenteditable="true"], [role="textbox"]').first
            await text_area.fill(f"{article_title}\n\n{article_content}")
            await page.wait_for_timeout(500)
            
            # Submit/Save source
            submit_btn = page.locator('button:has-text("Insert"), button:has-text("插入"), button:has-text("Save"), button:has-text("Add"), button:has-text("新增")').first
            await submit_btn.click(timeout=10000)
            await page.wait_for_timeout(3000)
            
            # 4. Navigate to Audio Overview
            print("🎙️ Opening Audio Overview...")
            audio_btn = page.locator('button:has-text("Audio Overview"), button:has-text("語音"), [aria-label*="Audio"]').first
            await audio_btn.click(timeout=10000)
            await page.wait_for_timeout(2000)
            
            # 5. Set language to Traditional Chinese and length to Short
            print("⚙️ Setting language and length...")
            # Look for customize/settings button
            customize_btn = page.locator('button:has-text("Customize"), button:has-text("自訂"), button:has-text("設定")').first
            try:
                await customize_btn.click(timeout=5000)
                await page.wait_for_timeout(1000)
                
                # Select Traditional Chinese
                lang_select = page.locator('text=繁體中文, text=Traditional Chinese').first
                await lang_select.click(timeout=5000)
                
                # Select Short length
                short_btn = page.locator('text=Short, text=短, [value="short"]').first
                await short_btn.click(timeout=5000)
                
                # Apply
                apply_btn = page.locator('button:has-text("Apply"), button:has-text("套用"), button:has-text("Done"), button:has-text("完成")').first
                await apply_btn.click(timeout=5000)
                await page.wait_for_timeout(1000)
            except Exception as e:
                print(f"⚠️ Customize step might have failed: {e}")
            
            # 6. Generate
            print("🎵 Generating audio (this may take ~10 minutes)...")
            generate_btn = page.locator('button:has-text("Generate"), button:has-text("產生"), button:has-text("生成")').first
            await generate_btn.click(timeout=10000)
            
            # Wait for generation (up to 12 minutes)
            start_time = time.time()
            while time.time() - start_time < NOTEBOOKLM_WAIT_SECONDS:
                # Check for download button or play button appearing
                download_btn = page.locator('button:has-text("Download"), button:has-text("下載"), [aria-label*="download"], [aria-label*="下載"]')
                if await download_btn.count() > 0:
                    print("✅ Audio generated!")
                    break
                
                elapsed = int(time.time() - start_time)
                if elapsed % 30 == 0:
                    print(f"   ⏳ Waiting... ({elapsed}s elapsed)")
                
                await page.wait_for_timeout(5000)
            
            # 7. Download
            print("💾 Downloading audio...")
            async with page.expect_download(timeout=30000) as download_info:
                await download_btn.first.click()
            
            download = await download_info.value
            await download.save_as(str(output_path))
            print(f"✅ Audio saved to: {output_path}")
            
            # Save cookies again (might have refreshed)
            await save_cookies(context)
            
            return output_path
            
        except Exception as e:
            print(f"❌ Error during NotebookLM automation: {e}")
            # Take screenshot for debugging
            debug_path = OUTPUT_DIR / "debug_screenshot.png"
            await page.screenshot(path=str(debug_path))
            print(f"📸 Debug screenshot saved to {debug_path}")
            return None
            
        finally:
            await browser.close()


async def main(article_title: str = None, article_content: str = None):
    import sys
    
    if "--login" in sys.argv:
        await manual_login()
        return
    
    if not article_title:
        # Load from step 1 output
        import json
        from datetime import date
        articles_file = OUTPUT_DIR / f"articles_{date.today().isoformat()}.json"
        if articles_file.exists():
            with open(articles_file, encoding="utf-8") as f:
                articles = json.load(f)
            if articles:
                article_title = articles[0]["title"]
                article_content = articles[0]["content"]
        
    if not article_title:
        print("❌ No article found. Run step 1 first.")
        return
    
    output_path = OUTPUT_DIR / "podcast_raw.wav"
    result = await generate_podcast(article_title, article_content, output_path)
    
    if result:
        print(f"🎉 Podcast generated: {result}")
    else:
        print("❌ Failed to generate podcast")


if __name__ == "__main__":
    asyncio.run(main())
