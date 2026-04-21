from use_cases.summarize_document import SummarizeDocumentUseCase
from domain.models import Document, Summary
from domain.interfaces import AISummarizer


class MockAI(AISummarizer):
    def summarize(self, doc: Document) -> Summary:
        return Summary(raw_text="這是摘要", word_count=4, model_name="Mock")


def test_summarize_use_case():
    mock_ai = MockAI()
    app = SummarizeDocumentUseCase(ai_service=mock_ai)

    result = app.execute("這是一個很短的文件內容", "短測試")
    assert result.raw_text == "這是一個很短的文件內容"

    result2 = app.execute(
        "這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容這是一個很長很長很長的文件內容",
        "長測試",
    )
    assert result2.raw_text == "這是摘要"

    print("[Success] Use Case 邏輯測試完成---------")


if __name__ == "__main__":
    test_summarize_use_case()
