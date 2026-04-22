from domain.models import Document, Summary
from domain.interfaces import AISummarizer


class SummarizeDocumentUseCase:
    def __init__(self, ai_service: AISummarizer):
        self.ai_service = ai_service

    # execute 為主要入口
    def execute(self, text: str, source: str) -> Summary:

        # PM需求: 超過50字摘要，不然不需要
        if len(text) > 50:
            doc = Document(content=text, source=source)
            return self.ai_service.summarize(doc)  # Document -> Summary
        else:
            return Summary(
                raw_text=text,
                word_count=len(text),
                model_name="N/A (over 500 to summary)",
            )
