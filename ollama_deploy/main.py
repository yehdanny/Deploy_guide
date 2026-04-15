import requests
import json

def ask_stream(prompt):
    url = "http://127.0.0.1:11434/api/generate"  # ✅ 11434
    print(f"post target: {url}")
    print('-'*50)
    payload = {
        "model": "qwen3:4b-instruct",              # ✅ 完整模型名稱
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    result = response.json()
    print(result.get("response"))

if __name__ == "__main__":
    ask_stream("用50字簡單解釋一下 Transformer")
