import requests
import json
__filename__ = __file__

class OllamaProvider:
    def __init__(self, host="127.0.0.1", port=11434):
        """
        ollama provider 的初始化，包含url和port，使用/chat接口。
        
        params:
            host: str
            port: int
        """
        self.url = f"http://{host}:{port}/api/chat"
        self.model_name = "qwen3:4b-instruct"

    def fetch_chat(self, messages:list):
        """
        用http post呼叫ollama取得回覆。

        params:
            messages: list, 格式為 [{"role": "user", "content": "..."} * N]
        return:
            str
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False
        }

        try:
            # Post & check HTTP status code
            response = requests.post(self.url, json=payload)
            response.raise_for_status() 
            result = response.json()
            print(f"[debug] {__filename__} : {result}")
            return result.get("message", {}).get("content", "")
        except requests.exceptions.RequestException as e:
            return f"[failed] {__filename__} : {str(e)}"
        
if __name__ == "__main__":
    provider = OllamaProvider()
    print(f"[test] {__filename__}\n")
    print(provider.fetch_chat([{"role": "user", "content": "你好，請自我介紹"}]))