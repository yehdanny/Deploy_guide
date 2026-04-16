from fastapi import FastAPI
import redis
import uuid
import json

app = FastAPI()
# 連接 Redis 容器
r = redis.Redis(host="redis-server", port=6379, db=0)


@app.get("/")
async def root():
    return {"message": "Welcome to the AI Task Queue API"}


@app.post("/ask")
async def ask_ai(prompt: str):
    task_id = str(uuid.uuid4())  # 生成唯一的任務 ID
    task_data = {"task_id": task_id, "prompt": prompt}

    # 將任務推入名為 'ai_tasks' 的隊列中
    r.lpush("ai_tasks", json.dumps(task_data))

    # 立即回傳 ID 給使用者，不等待 AI 運算
    return {"status": "Task queued", "task_id": task_id}


@app.get("/result/{task_id}")
async def get_result(task_id: str):
    # 從 Redis 查詢處理完的結果
    result = r.get(f"result:{task_id}")
    if result:
        return {"task_id": task_id, "answer": result.decode("utf-8")}
    return {"status": "Processing or not found"}
