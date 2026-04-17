from fastapi import FastAPI
import redis
import uuid
import json
import httpx

app = FastAPI()
r = redis.Redis(host="redis-server", port=6379, db=0)
# 服務發現
AUDIT_SERVICE_URL = "http://audit-service:8000/log"


@app.get("/")
async def root():
    return {"message": "service discovery API-healthy"}


@app.post("/ask")
async def ask_ai(prompt: str) -> dict:
    task_id = str(uuid.uuid4())
    # audit
    async with httpx.AsyncClient() as Clinet:
        try:
            await Clinet.post(
                AUDIT_SERVICE_URL,
                json={"task_id": task_id, "action": "received_request"},
            )
        except Exception as e:
            print(f"[error] AUDIT service : {e}")

    # redis
    r.lpush("ai_tasks", json.dumps({"task_id": task_id, "prompt": prompt}))
    return {"status": "Task queued", "task_id": task_id}


@app.get("/result/{task_id}")
async def get_result(task_id: str):
    # 從 Redis 查詢處理完的結果
    result = r.get(f"result:{task_id}")
    if result:
        return {"task_id": task_id, "answer": result.decode("utf-8")}
        # decode("utf-8") -> "prompt": "\\u4f60\\u597d\\uff01\\u8acb\\u7528\\u4e00\\u53e5\\u8a71\\u4ecb\\u7d39\\u4f60\\u81ea\\u5df1\\u3002"}
    return {"status": "Nothing return"}
