import requests
from domain.models import Document, Summary
from domain.interfaces import AISummarizer


class OllamaSummarizer(AISummarizer):
    SUPPORTED_MODELS = [
        "llama3:latest",
        "qwen3:4b-instruct",
        "qwen3:4b-instruct-2507-fp16",
        "codellama:latest",
        "deepseek-coder:latest",
    ]

    def __init__(self, model_name: str = "qwen3:4b-instruct-2507-fp16"):
        if model_name not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"\n[infrastructure:ollama_adapter:__init__] Unsupported model name: {model_name}, please use one of {self.SUPPORTED_MODELS}\n"
            )

        self.model_name = model_name
        self.url = "http://localhost:11434/api/generate"

    def summarize(self, doc: Document) -> Summary:
        payload = {
            "model": self.model_name,
            "prompt": f"請幫我條列式摘要成三行以內的內容：{doc.content}",
            "stream": False,
        }
        response = requests.post(self.url, json=payload)
        response.raise_for_status()
        ai_answer = response.json().get("response", "error")

        return Summary(
            raw_text=ai_answer, word_count=len(ai_answer), model_name=self.model_name
        )
