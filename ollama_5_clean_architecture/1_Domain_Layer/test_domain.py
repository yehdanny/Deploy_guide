# test_domain.py (放在最外層測試用)
from domain.models import Document
from domain.interfaces import AISummarizer


def test_setup():
    my_doc = Document(content="哈囉 Ollama", source="測試")
    print(f"成功建立了實體：{my_doc.content}")


def test_interface():
    try:
        my_interface = AISummarizer()
        print(f"成功建立了介面：{my_interface}")
    except Exception:
        print(
            "執行失敗是正常的，因為我們不應該呼叫藍圖。"
            "應該等之後的實作者來呼叫這個藍圖 "
            "，用這個藍圖的格式當作schema。"
        )


if __name__ == "__main__":
    test_setup()
    test_interface()
