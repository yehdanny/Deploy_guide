import asyncio #gather、run用
import time
from ollama import AsyncClient #ollama generate 用

async def fetch_generate(prompt:str, task_id:int):
    print(f"[task] {task_id}----start")
    start_time = time.perf_counter()

    response = await AsyncClient().generate(model='qwen3:4b-instruct', prompt=prompt)
    
    end_time = time.perf_counter()
    print(f"[task] {task_id}----end cost {end_time - start_time:.2f}s")

    return response.get("response","")

async def run():
    prompts = [
        "請用一句話解釋什麼是量子力學。",
        "請用一句話解釋什麼是深度學習。",
        "請用一句話解釋什麼是遞迴。",
        "請用一句話解釋什麼是區塊鏈。",
        "請用一句話解釋什麼是相對論。"
    ]
    print("--- 併發請求 ---")
    start_all = time.perf_counter()

    tasks = [fetch_generate(p, id) for id, p in enumerate(prompts)] #逐個併發
    # print(f"[info] {task}")
    results = await asyncio.gather(*tasks) #gather同時執行所有任務

    print("\n--- 所有結果 ---")
    for i, res in enumerate(results):
        print(f"{i+1}. {res.strip()}")
    
    print(f"\n總共花費時間: {time.perf_counter() - start_all:.2f}s")


if __name__ == "__main__":
    asyncio.run(run())