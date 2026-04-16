import asyncio
from ollama import AsyncClient
import time

SEMAPHORE =  asyncio.Semaphore(2)
TIMEOUT = 60.0
async def mock_rag(keyword:str):
    await asyncio.sleep(1.5)
    return f"來自 {keyword} 的查詢結果。"

async def run_task(task_id:int,model:str, prompt:str):
    async with SEMAPHORE :
        try:
            print(f'[info] Running {task_id}')
            response = await asyncio.wait_for(
                AsyncClient().generate(model=model, prompt=prompt),
                timeout = TIMEOUT
            )
            print('semaphore---------')
            return response.get('response')
        except asyncio.TimeoutError:
            print(f'[timeout]')
        except Exception as e:
            print(f'others error : {e}')
        

async def main():
    start_time = time.perf_counter()

    #rag
    knowledge = [mock_rag("台大牙科"),mock_rag("高雄長庚牙科")]
    rag_knowledge = await asyncio.gather(*knowledge)
    context = "".join(rag_knowledge)

    prompt = f"根據以下背景：{context}，請提供50字簡短的診斷建議。"
    
    #llm
    tasks = [
        run_task(1, 'qwen3:4b-instruct', prompt),
        run_task(2, 'llama3', prompt),
        run_task(3, 'gemma2', prompt),
    ]
    
    response = await asyncio.gather(*tasks)
    merged_response = f"下面是專家的意見 :{'.'.join(response)}。幫我用繁體中文做一個總結。"
    
    #llm flush
    print("")
    async for msg in await AsyncClient().generate(model='llama3',prompt=merged_response,stream=True):
        print(msg.get('response'), end="", flush=True)

    total_duration = time.perf_counter() - start_time
    print(f"\n\n全程總耗時: {total_duration:.2f} 秒")

if __name__=="__main__":
    asyncio.run(main())