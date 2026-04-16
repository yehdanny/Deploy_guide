# 我的AI技能 - 總覽


## 一、AI技能

### 本儲存庫記錄我 AI 的實作過程，技能依序為：

- [deploy ollama](./ollama_deploy)
- [ollama api communication](./ollama_api_communication)
- [ollama async / concurrency](./ollama_3_async)

---
### 興趣相關

- [openclaw+discord](./openclaw+discord)

---
## 二、專案一覽

| 資料夾 | 說明 |
|--------|------|
| [`ollama_1_deploy`](./ollama_1_deploy) | 最小化範例：透過 Ollama 進行單次對話以 API 呼叫本地 LLM。 |
| [`ollama_2_api_communication`](./ollama_2_api_communication) | 進階範例：透過 Ollama 進行多輪對話的三層式對話系統，Service 保持 Stateless，可擴充為多使用者Web使用， API 使用 `/api/chat` 。 |
| [`ollama_3_async`](./ollama_3_async) | 進階範例：透過```AsyncClient```套件進行多請求呼叫，包含:非同步+併發、串流、限流、超時保護。 |
| [`openclaw+discord`](./openclaw+discord) | 使用openclaw串接discord，透過對discord的文字輸入，進行腳本生成、影片產製、音效合成到 YouTube 上傳的完整四階段 Pipeline。 |

## 三、大方向

- **本地推理**：
    - `ollama_1_deploy` 為入門範例
    - `ollama_2_api_communication` 則是可擴充的對話服務骨架
    - `ollama_3_async` 則是多人請求進階範例
- **內容自動化**：`openclaw+discord` 展示從腳本生成、影片產製、音效合成到 YouTube 上傳的完整四階段 Pipeline。

各子專案內皆附有獨立的 `README.md`，詳細說明環境需求、安裝與使用方式。
