from fastapi import FastAPI
from dotenv import load_dotenv
from .database import SessionLocal, AIResult
import redis
import uuid
import json
import httpx


load_dotenv()

app = FastAPI()
r = redis.Redis(host="redis-server", port=6379, db=0)
# 服務發現
AUDIT_SERVICE_URL = "http://audit-service:8000/log"


@app.get("/")
async def root():
    return {"message": "service discovery API-healthy"}


@app.post("/ask")
async def ask_ai(prompt: str, model: str = "qwen3:4b-instruct") -> dict:
    task_id = str(uuid.uuid4())
    # audit
    async with httpx.AsyncClient() as Clinet:
        try:
            await Clinet.post(
                AUDIT_SERVICE_URL,
                json={"task_id": task_id, "action": "received_request"},
            )
        except Exception as e:
            print(f"[error] Audit Service down. {e}")

    # redis
    r.setex(f"status:{task_id}", 3600, "waiting")  # setex -> set waiting
    r.lpush(
        "ai_tasks", json.dumps({"task_id": task_id, "prompt": prompt, "model": model})
    )
    return {"status": "Task queued", "task_id": task_id}


@app.get("/result/{task_id}")
async def get_result(task_id: str):

    # 從 database 查詢處理完的結果
    db = SessionLocal()
    record = db.query(AIResult).filter(AIResult.task_id == task_id).first()

    if record:
        return {
            "task_id": task_id,
            "status": "completed",
            "result": record.answer,
        }
    else:
        result = r.get(f"status:{task_id}")
        status = r.get(f"status:{task_id}")
        return {
            "task_id": task_id,
            "status": status.decode("utf-8"),
            "result": result.decode("utf-8") if result else None,
        }
