# 我的AI技能 - async / concurrency 篇

---


階段一：基礎非同步併發實作 [async concurrency](./ollama_async_concurrency.py)
```bash
uv add ollama
```
環境建置： 學習如何安裝並使用非同步版本的 Client 端庫（如 ollama.AsyncClient）。

定義協程 (Coroutine)： 使用 async def 定義一個封裝 Ollama 請求的函式，並理解 await 的放置位置。

單一非同步呼叫： 練習在不阻塞主線程的情況下，發送一次請求並獲取結果。

### > 非同步+併發 使總花費時間更短
![alt text](image.png)

---