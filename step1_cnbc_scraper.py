"""
Step 1: Scrape today's CNBC AI articles.
Uses requests for article list, then newspaper3k/trafilatura for content extraction.
"""
import sys, io
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
if sys.stderr and hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import json
import re
from config import CNBC_AI_URL, OUTPUT_DIR

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_today_articles():
    """Scrape CNBC AI page for today's articles."""
    resp = requests.get(CNBC_AI_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "lxml")
    articles = []
    
    # CNBC article cards
    for card in soup.select("div.Card-titleContainer a, a.Card-title"):
        title = card.get_text(strip=True)
        url = card.get("href", "")
        if not url.startswith("http"):
            url = "https://www.cnbc.com" + url
        if title and url:
            articles.append({"title": title, "url": url})
    
    if not articles:
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "/2026/" in href or "/2025/" in href:
                title = a_tag.get_text(strip=True)
                if title and len(title) > 20:
                    url = href if href.startswith("http") else "https://www.cnbc.com" + href
                    articles.append({"title": title, "url": url})
    
    # Deduplicate and filter out video-only pages
    seen = set()
    unique = []
    for a in articles:
        if a["url"] not in seen and "/video/" not in a["url"]:
            seen.add(a["url"])
            unique.append(a)
    
    return unique


def get_article_content(url):
    """
    Fetch full article text using trafilatura (better at extracting 
    main content from JS-heavy sites).
    Falls back to basic extraction if trafilatura is not available.
    """
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            if text:
                return text
    except ImportError:
        pass
    
    # Fallback: requests + BeautifulSoup with broader selectors
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    
    # Try multiple selectors
    for selector in [
        "div.ArticleBody-articleBody",
        "div.group",
        "div[data-module='ArticleBody']",
        "article",
    ]:
        body = soup.select_one(selector)
        if body:
            paragraphs = body.find_all("p")
            text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            if text:
                return text
    
    # Last resort: grab all <p> with substantial text
    all_p = soup.find_all("p")
    long_p = [p.get_text(strip=True) for p in all_p if len(p.get_text(strip=True)) > 50]
    if long_p:
        return "\n\n".join(long_p)
    
    return ""


def main():
    print("[Step1] Scraping CNBC AI articles...")
    articles = get_today_articles()
    
    print(f"[Step1] Found {len(articles)} articles")
    for i, a in enumerate(articles):
        print(f"  {i+1}. {a['title'][:80]}")
        try:
            content = get_article_content(a["url"])
            a["content"] = content
            print(f"     -> Content fetched ({len(content)} chars)")
        except Exception as e:
            a["content"] = ""
            print(f"     -> Failed to fetch: {e}")
    
    # Save
    output_file = OUTPUT_DIR / f"articles_{date.today().isoformat()}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"[Step1] Saved to {output_file}")
    return articles


if __name__ == "__main__":
    main()
