# deploy

本儲存庫集中管理多個 AI 相關的部署與自動化專案，涵蓋本地模型推理、對話服務，以及 YouTube Shorts 自動生成 Pipeline。

## 專案一覽

| 資料夾 | 說明 |
|--------|------|
| [`ollama_deploy`](./ollama_deploy) | 最小化範例：透過 Ollama 進行單次對話以 API 呼叫本地 LLM。 |
| [`ollama_api_communication`](./ollama_api_communication) | 進階範例：透過 Ollama 進行多輪對話的三層式對話系統，Service 保持 Stateless，可擴充為多使用者Web使用， API 使用 `/api/chat` 。 |
| [`openclaw+discord`](./openclaw+discord) | 使用openclaw串接discord，透過對discord的文字輸入，進行腳本生成、影片產製、音效合成到 YouTube 上傳的完整四階段 Pipeline。 |

## 大方向

- **本地推理**：`ollama_deploy` 為入門範例，`ollama_api_communication` 則是可擴充的對話服務骨架。
- **內容自動化**：`openclaw+discord` 展示從腳本生成、影片產製、音效合成到 YouTube 上傳的完整四階段 Pipeline。

各子專案內皆附有獨立的 `README.md`，詳細說明環境需求、安裝與使用方式。
