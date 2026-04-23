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
        我要你判斷一段話的情緒，並解釋原因。
        範例 1：
        用戶：『這部電影特效很好，但劇情簡直是災難。』
        推理：特效正評 (+1)，劇情負評 (-2)，整體偏向負面。
        結論：【偏向負面】

        範例 2：
        用戶：『這家餐廳排隊排很久，但吃到第一口肉時我覺得一切都值得了。』
        推理：[請依照範例 1 的邏輯補完推理過程]
        結論：
    """
    print(cot_bot.chat(fewshot_prompt))
