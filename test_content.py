import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

import requests
from bs4 import BeautifulSoup

url = "https://www.cnbc.com/2026/03/27/openai-ads-pilot-tops-100-million-in-annualized-revenue-in-under-2-months.html"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

r = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(r.text, "lxml")

# Try various selectors
selectors = [
    "div.ArticleBody-articleBody",
    "div.group",
    "div[data-module='ArticleBody']",
    "article",
    "div.ArticleBody",
    "div.RenderKeyPoints-list",
    "div.FeaturedContent-wrapper",
]

for sel in selectors:
    found = soup.select(sel)
    print(f"Selector: {sel} -> {len(found)} matches")
    if found:
        text = found[0].get_text(strip=True)[:200]
        print(f"  Preview: {text}")

# Try all divs with many <p> children
print("\n--- Divs with many <p> tags ---")
for div in soup.find_all("div"):
    ps = div.find_all("p", recursive=False)
    if len(ps) >= 3:
        cls = div.get("class", [])
        print(f"  div.{'.'.join(cls) if cls else '(no class)'} -> {len(ps)} paragraphs")
        for p in ps[:2]:
            print(f"    {p.get_text(strip=True)[:100]}")
        break
