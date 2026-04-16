from fastapi import FastAPI
import httpx

app = FastAPI()

# 這是 Ollama 在 Docker 環境中存取宿主機的特殊位址
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"


@app.get("/")
async def root():
    return {"message": "AI Microservice is running"}


@app.post("/ask")
async def ask_ai(prompt: str):
    payload = {
        "model": "qwen3:4b-instruct",  # 確保你本機有先 pull 這個模型
        "prompt": prompt,
        "stream": False,
    }

    async with httpx.AsyncClient() as client:  # 防止塞車，可進出
        # 設定較長的 timeout，因為 AI 推論需要時間
        response = await client.post(OLLAMA_URL, json=payload, timeout=60.0)
        return response.json()
