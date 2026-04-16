import redis
import json
import httpx
import time

r = redis.Redis(host="redis-server", port=6379, db=0)
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"


def process_tasks():
    print("Worker started, waiting for tasks...")
    while True:
        # 從隊列右側取出任務 (Blocking pop)
        _, task_json = r.brpop("ai_tasks")
        task = json.loads(task_json)
        task_id = task["task_id"]
        prompt = task["prompt"]

        print(f"Processing task: {task_id}")

        # 呼叫 Ollama
        try:
            with httpx.Client() as client:
                response = client.post(
                    OLLAMA_URL,
                    json={
                        "model": "qwen3:4b-instruct",
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=120.0,
                )
                answer = response.json().get("response", "No response")

                # 將結果存回 Redis，設定 1 小時後自動刪除 (省空間)
                r.setex(f"result:{task_id}", 3600, answer)
                print(f"Task {task_id} completed.")
        except Exception as e:
            r.setex(f"result:{task_id}", 3600, f"Error: {str(e)}")


if __name__ == "__main__":
    process_tasks()
