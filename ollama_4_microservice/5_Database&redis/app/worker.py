import redis
import json
import httpx
import time

from .database import SessionLocal, AIResult


def process_tasks(local=False) -> dict:
    # 取得redis的資料，while r.brpop 用httpx Client().generate()
    # return response.json().get()
    if local:
        r = redis.Redis(host="localhost", port=6379, db=0)
        ollama_url = "http://localhost:11434/api/generate"
    else:
        r = redis.Redis(host="redis-server", port=6379, db=0)
        ollama_url = "http://host.docker.internal:11434/api/generate"  # internal 別拼錯
    while True:
        try:
            _, queue_data_json = r.brpop("ai_tasks")
            queue_data = json.loads(queue_data_json)
            task_id = queue_data["task_id"]
            prompt = queue_data["prompt"]
            model = queue_data["model"]

            # setex -> set processing
            print(f"[debug] processing task {task_id}")
            r.setex(f"status:{task_id}", 3600, "processing")

            with httpx.Client() as client:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                }
                response = client.post(url=ollama_url, json=payload, timeout=120.0)
                answer = response.json().get("response", "error")

                # postgresql
                db = SessionLocal()
                db.add(
                    AIResult(task_id=task_id, prompt=prompt, model=model, answer=answer)
                )
                db.commit()

                # setex -> set completed
                r.setex(f"result:{task_id}", 3600, answer)
                r.setex(f"status:{task_id}", 3600, "completed")

                # print(f"[debug] {response.json()}")
                print(f"Task {task_id} completed.")

        except Exception as e:
            r.setex(f"result:{task_id}", 3600, str(e))
            r.setex(f"status:{task_id}", 3600, "error")  # setex -> set error
            print(f"Worker Loop Error (可能是 Redis 連線失敗): {e}")
            time.sleep(5)  # 出錯時等待 5 秒後重試，避免程式直接崩潰
        finally:
            db.close()


if __name__ == "__main__":
    # 本地測試要先起一個redis : docker run -d -p 6379:6379 redis
    local_mode = False  # 若要本地運行，請設為 True

    if local_mode:
        # 單機測試：嘗試發送一個任務進去
        r_test = redis.Redis(host="localhost", port=6379, db=0)
        test_task = {"task_id": "test_123", "prompt": "你好！請用一句話介紹你自己。"}
        try:
            r_test.lpush("ai_tasks", json.dumps(test_task))
            print(f"已發送測試任務到隊列: {test_task['task_id']}")
        except Exception as e:
            print(f"發送測試任務失敗 (也許是在本地端執行連不到 Redis): {e}")

    process_tasks(local=local_mode)
