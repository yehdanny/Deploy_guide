class ChatSession:
    def __init__(self, system_prompt="你是一個專業的客服人員。"):
        self.system_prompt = system_prompt
        self.history = []
        self.reset()

    def reset(self):
        """
        初始化時放入 System Prompt。
        """
        self.history = [{"role": "system", "content": self.system_prompt}]

    def add_user_message(self, content):
        """
        新增使用者的訊息到對話紀錄中。
        """
        self.history.append({"role": "user", "content": content})

    def add_ai_message(self, content):
        """
        新增AI的訊息到對話紀錄中。
        """
        self.history.append({"role": "assistant", "content": content})

    def get_messages(self):
        """
        回傳完整的對話紀錄。
        """
        return self.history