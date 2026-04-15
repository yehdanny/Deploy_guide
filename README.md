# deploy

本儲存庫集中管理多個 AI 相關的部署與自動化專案，涵蓋本地模型推理、對話服務，以及 YouTube Shorts 自動生成 Pipeline。

## 專案一覽

| 資料夾 | 說明 |
|--------|------|
| [`ollama_deploy`](./ollama_deploy) | 最小化範例：透過 Ollama 本地 API 以串流方式呼叫本地 LLM（預設 `qwen3.5:35b-a3b`），逐字輸出回應。 |
| [`ollama_api_communication`](./ollama_api_communication) | 基於 Ollama `/api/chat` 的三層式對話系統（Infrastructure / Application / Data），Service 保持 Stateless，方便擴充為多使用者 Web 服務。 |
| [`openclaw+discord`](./openclaw+discord) | Animal Shorts — AI 動物對決 YouTube Shorts 自動生成 Pipeline，結合 Kling AI 瀏覽器自動化生成影片，並透過 YouTube Data API v3 自動上傳。 |

## 大方向

- **本地推理**：`ollama_deploy` 為入門範例，`ollama_api_communication` 則是可擴充的對話服務骨架。
- **內容自動化**：`openclaw+discord` 展示從腳本生成、影片產製、音效合成到 YouTube 上傳的完整四階段 Pipeline。

各子專案內皆附有獨立的 `README.md`，詳細說明環境需求、安裝與使用方式。
