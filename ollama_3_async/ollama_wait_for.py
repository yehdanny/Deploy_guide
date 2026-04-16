import asyncio
import sys
from ollama import AsyncClient

async def risky_ollama_task(task_id, prompt:str, timeout_limit:float):
    try:
        print(f"Task {task_id} started...")
        response = await asyncio.wait_for(
            AsyncClient().generate(model='qwen3:4b-instruct', prompt=prompt),
            timeout=timeout_limit
        )
        print(f"✅ [任務 {task_id}] 成功完成！")
        return response.get('response')
    except asyncio.TimeoutError:
        print(f"[time out error]")
        return None
    except Exception as e:
        # 處理其他可能的錯誤（如 Ollama 未啟動）
        print(f"[error] : {e}")
        return None

async def main():
    print("--- [Ex-05] Timeout 錯誤處理練習 ---")
    
    # 模擬兩個任務：一個給予充足時間，一個設定極短時間
    tasks = [
        risky_ollama_task(1, "請寫一段 500 字的長文。", timeout_limit=0.5), # 故意設極短
        risky_ollama_task(2, "哈囉！", timeout_limit=30.0)                 # 充足時間
    ]
    response = await asyncio.gather(*tasks)
    for i, res in enumerate(response):
        status = "成功" if res else "失敗/超時"
        print(f"任務 {i+1}: {status}")

if __name__ == "__main__":
    asyncio.run(main())