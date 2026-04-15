from init_ollama import OllamaProvider
from session_manager import ChatSession
__filename__ = __file__

class Service:
    def __init__(self):
        """
        服務的初始化階段，將所有功能初始化，包含provider的初始化。
        """
        
        self.provider = OllamaProvider(host="127.0.0.1", port=11434)
        self.system_prompt = "你是一個專業客服，請用繁體中文回答，內容約30字，嚴禁透露你的架構細節。"
        self.session = ChatSession(self.system_prompt)
    
    def _check_input(self, prompt:str):
        """
        特定詞彙觸發除錯模式
        """
        if not prompt:
            return True
        elif prompt == "/reset":
            self.session.reset()
            print("[debug] History cleared.")
            return True
        elif prompt == "/history":
            print(self.session.get_messages())
            return True
        return False
    
    def run(self):
        """
        服務的執行階段，接收使用者的輸入，並將其傳送給ollama，最後將結果輸出。
        """
        #取當前&歷史對話
        prompt = input("User: ")
        #檢查是否為除錯指令或輸入錯誤
        if self._check_input(prompt): return #出口

        #更新狀態
        self.session.add_user_message(prompt)

        #api
        provider_response = self.provider.fetch_chat(self.session.get_messages())
        print(f"Chatbot: {provider_response}")

        #更新狀態
        self.session.add_ai_message(provider_response)
        return #出口

if __name__ == "__main__":
    service = Service()
    while True:
        service.run()
