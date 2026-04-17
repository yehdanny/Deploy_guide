import redis
import json
import httpx
import time


# r = redis.Redis(host="redis-server", port=6379, db=0)
def process_tasks(local=False):
    # 根據 local 參數設定連線
    if local:
        r = redis.Redis(host="localhost", port=6379, db=0)
        ollama_url = "http://localhost:11434/api/generate"
        print("=== Worker Started (本地運行模式) ===")
    else:
        r = redis.Redis(host="redis-server", port=6379, db=0)
        ollama_url = "http://host.docker.internal:11434/api/generate"
        print("=== Worker Started (Docker 模式) ===")

    print("Worker is waiting for tasks...")
    while True:
        try:
            # 從隊列右側取出任務 (Blocking pop)
            _, task_json = r.brpop("ai_tasks")
            task = json.loads(task_json)
            task_id = task["task_id"]
            prompt = task["prompt"]

            print(f"Processing task: {task_id}")

            # 呼叫 Ollama
            with httpx.Client() as client:
                response = client.post(
                    ollama_url,
                    json={
                        "model": "qwen3:4b-instruct",
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=120.0,
                )
                print(f"[debug] {response.json()}")
                answer = response.json().get("response", "No response")

                # 將結果存回 Redis，設定 1 小時後自動刪除 (省空間)
                r.setex(f"result:{task_id}", 3600, answer)
                print(f"Task {task_id} completed.")
        except Exception as e:
            print(f"Worker Loop Error (可能是 Redis 連線失敗): {e}")
            time.sleep(5)  # 出錯時等待 5 秒後重試，避免程式直接崩潰


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

# 已發送測試任務到隊列: test_123
# === Worker Started (本地運行模式) ===
# Worker is waiting for tasks...
# Processing task: test_123
# [debug] {'model': 'qwen3:4b-instruct', 'created_at': '2026-04-17T01:25:07.8071923Z', 'response': '你好！我是Qwen，是阿里雲開發的超大型語言模型，能夠幫助你回答問題、創作文字、解決問題，並提供各種資訊與協助。',
