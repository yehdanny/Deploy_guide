# domain/interfaces.py
from abc import ABC, abstractmethod
from .models import Document, Summary


class AISummarizer(ABC):
    """
    這是一個『孔』(Port)。
    它定義了系統需要什麼樣的 AI 能力，但不關心它是怎麼實現的。
    """

    @abstractmethod
    def summarize(self, doc: Document) -> Summary:
        pass
