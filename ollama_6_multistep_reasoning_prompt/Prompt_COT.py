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
    cot_prompt = """
        請遵循以下格式回答：

    分析：列出題目給的所有已知數據。

    步驟：逐步計算數量的變化。

    結論：給出最終答案。    
    """
    print(cot_bot.chat(cot_prompt + input("請輸入題目：")))
