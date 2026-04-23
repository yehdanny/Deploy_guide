import requests


class OllamaChat:
    def __init__(self, model_name: str = "qwen3:4b-instruct-2507-fp16"):
        self.model_name = model_name
        self.url = "http://localhost:11434/api/generate"

    def chat(self, prompt: str) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }
        response = requests.post(self.url, json=payload)
        response.raise_for_status()
        ai_answer = response.json().get("response", "error")

        return ai_answer


if __name__ == "__main__":
    cot_bot = OllamaChat()
    fewshot_prompt = """
        請寫一段 Python 程式碼來反轉字串中的單詞順序，但保持標點符號位置不變。

        要求：

        草稿：先寫出初步的邏輯思維。

        檢查：檢查這個邏輯是否處理了多個標點符號相連的情況？是否有邊界案例（Edge cases）？

        優化：基於檢查結果，寫出最終的程式碼。
    """
    print(cot_bot.chat(fewshot_prompt))
