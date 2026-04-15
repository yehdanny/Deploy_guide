import asyncio
import sys
from ollama import AsyncClient

async def fetch_generate():
    print("--- [Ex-04] Ollama 串流處理練習 ---")
      
    prompt = "請寫一篇關於未來 AI 如何改變醫療影像診斷的短文（約 200 字）。"
    
    print(f"發送請求中...\n")
    print("AI 回應：", end="", flush=True)

    # 使用 async for 處理串流
    async for part in await AsyncClient().generate(model='qwen3:4b-instruct', prompt=prompt, stream=True):
        # 取得當前生成的文字片段
        content = part['response']
        print(content, end="", flush=True)

    print("\n\n--- 串流結束 ---")

if __name__ == "__main__":
    asyncio.run(fetch_generate())

# --- [Ex-04] Ollama 串流處理練習 ---
# 發送請求中...

# AI 回應：未來，人工智慧將深刻改變醫療影像診斷。AI 可在毫秒內分析海量影像資料，如X光、MRI與CT掃描，迅速識別病灶，如腫瘤、骨折或腦出血，精度甚至超越人類醫生。透過深度學習，AI 能持續自我優化，學習更多病例，提升診斷一致性與準確性。此外，AI 可協助醫生進行早期篩檢，例如在肺部影像中發現微小結節，提早發現肺癌。同時，它能減少醫生負擔，將繁重的影像篩選工作自動化，讓醫師專注於複雜病例與患者互動。未來，結合AI的智慧診斷系統將實現即時、個性化與普及化的醫療服務，大幅縮短診斷時間，提升預防與治療效率，為人類健康帶來革命性進步。

# --- 串流結束 ---