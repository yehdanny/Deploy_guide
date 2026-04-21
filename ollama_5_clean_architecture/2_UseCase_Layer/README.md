# UseCase Layer  | 編寫流程

### 還是不寫具體實作，只寫流程。

流程寫好後
- 先前定義的AISummarizer會被拿來當作藍圖。

```python
class AISummarizer(ABC):
    @abstractmethod
    def summarize(self, doc: Document) -> Summary:
        pass
```

- 未來會用`OllamaSummarizer`繼承`AISummarizer`。
    - <font color="orange">然後用自己的方式實作summarize覆蓋掉原本的summarize藍圖。</font>

```python
class OllamaSummarizer(AISummarizer):
    def __init__(self, model_name: str = "llama3"):
        ...
    def summarize(self, doc: Document) -> Summary:
        ...
```

- 我們寫的流程[Summarize_UseCase](./use_cases/summarize_document.py)則能使用任何繼承`AISummarizer`的物件。
    - <font color="orange">(因為任何繼承`AISummarizer`的物件都符合我們對`ai_service`的定義，
    故Usecase可使用)</font>

```python
class Summarize_UseCase:
    def __init__(self, ai_service: AISummarizer):
        self.ai_service = ai_service

    def execute(self, doc: Document) -> Summary:
        return self.ai_service.summarize(doc)
```

- 所以假如`OllamaSummarizer`之後要多新增`GeminiSummarizer`，我們完全不用改任何東西。

---

### [Mock測試](./Mock_test_usecase.py)

- 透過`MockAI`來模擬`OllamaSummarizer`，來測試`Summarize_UseCase`的邏輯。

- 透過創建`mock_ai`物件，並將其傳入`Summarize_UseCase`中，<font color="orange">再用execute就會進到我們寫的流程內。</font>

```python

def test_summarize_use_case():
    mock_ai = MockAI()
    app = SummarizeDocumentUseCase(ai_service=mock_ai)

    result = app.execute("這是一個很短的文件內容", "短測試")

```