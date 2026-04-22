# Domain Layer  | 規格書

1. models內定義需要什麼物件、物件型態

2. interfaces內定義需要什麼功能(寫輸入輸出格式，具體實作不寫)

### 先寫起來後面用繼承方法實作(ex:OllamaSummarizer繼承AISummarizer)

```python
class OllamaSummarizer(AISummarizer):
    def __init__(self, model_name: str = "llama3"):
        ...init...

    def summarize(self, doc: Document) -> Summary:
        ...覆蓋的method...

```



---

### 目標：定義「規則」，完全不寫任何實作邏輯。

在這個階段，你甚至不需要安裝 `requests` 或 `ollama` 套件，只需構想需求、儲存的狀態。
* **實體 (Entities)**：定義資料模型。
* **抽象介面 (Interfaces)**：定義 AI 服務應該具備什麼功能。
* **成果**：
    - 地基(models.py) : 會有一個Document和Summary。各自要包含什麼變數。
    - 藍圖(interfaces.py) : 會有一個summarize功能，輸入Document型別，輸出Summary型別。
