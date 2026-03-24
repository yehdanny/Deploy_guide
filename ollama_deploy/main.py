import requests
import json

def ask_stream(prompt):
    url = "http://127.0.0.1:11434/api/generate"  # ✅ 11434
    print(f"post target: {url}")
    print('-'*50)
    payload = {
        "model": "qwen3.5:35b-a3b",              # ✅ 完整模型名稱
        "prompt": prompt,
        "stream": True
    }
    with requests.post(url, json=payload, stream=True) as r:
        for line in r.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:            # ✅ 防止 key 不存在報錯
                    print(data["response"], end="", flush=True)

if __name__ == "__main__":
    ask_stream("解釋一下 Transformer")
