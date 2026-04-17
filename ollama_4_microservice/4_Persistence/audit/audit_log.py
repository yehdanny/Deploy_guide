from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class LogEntry(BaseModel):
    task_id: str
    action: str


@app.post("/log")
async def record_log(entry: LogEntry):  # Dependency Injection自動拿取entry
    # 在真實場景中，這裡會寫入資料庫
    print(f"[AUDIT LOG] Task: {entry.task_id} | Action: {entry.action}")
    return {"status": "Logged"}
