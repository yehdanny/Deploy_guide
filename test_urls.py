import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
data = json.load(open('output/articles_2026-03-27.json', 'r', encoding='utf-8'))
for a in data[:5]:
    print(a['url'])
