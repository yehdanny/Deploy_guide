# domain/models.py
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)  # 使用 frozen 確保實體不可變，符合 Clean Architecture 精神
class Document:
    content: str
    source: str
    language: str = "zh-TW"


@dataclass(frozen=True)
class Summary:
    raw_text: str
    word_count: int
    model_name: str  # 雖然不知道哪個模型，但我們預留欄位存放結果
