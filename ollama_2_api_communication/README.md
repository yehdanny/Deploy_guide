# 我的AI技能 - API Communication 篇

---

## Ollama API Communication

一個基於 Ollama `/api/chat` 接口的輕量級對話系統，採用三層架構設計，符合 **Stateless API** 與 **Separation of Concerns** 原則，方便未來擴充為多使用者 Web 服務。

---

## 專案架構

本系統拆分為三個主要模組，對應三層職責：

| 檔案 | 類別 | 分層 | 職責 |
|------|------|------|------|
| `init_ollama.py` | `OllamaProvider` | Infrastructure Layer | 底層 HTTP 通訊，負責與 Ollama 引擎的 Request 發送與 Response 解析 |
| `service.py` | `Service` | Application Layer | 業務邏輯、使用者輸入處理、除錯指令 (`/reset`、`/history`) 與 System Prompt 模板化 |
| `session_manager.py` | `ChatSession` | Data Layer | 維護對話狀態與歷史紀錄 (History Management)，讓邏輯層不需處理資料結構 |

這種分層的優點：
- **Service 保持 Stateless**：狀態全數交由 `ChatSession` 管理，未來可水平擴展。
- **多人使用不打架**：每個使用者擁有獨立的 `ChatSession` 實例，互不干擾。
- **可替換性高**：更換模型引擎時只需改寫 `OllamaProvider`，不影響上層邏輯。

---

## 環境需求

- Python >= 3.12
- 本機或遠端已啟動的 [Ollama](https://ollama.com/) 服務 (預設 `127.0.0.1:11434`)
- 已 pull 所需模型 (預設 `qwen3:4b-instruct`)

```bash
ollama pull qwen3:4b-instruct
ollama serve
```

## 安裝

使用 `uv` (推薦)：

```bash
uv sync
```

或使用 pip：

```bash
pip install -r requirements.txt  # 或: pip install "requests>=2.33.1"
```

---

## 使用方式

### 啟動互動式對話

```bash
python service.py
```

對話指令：

| 指令 | 說明 |
|------|------|
| `/reset` | 清除目前對話歷史，保留 System Prompt |
| `/history` | 印出完整對話紀錄 (含 system、user、assistant) |
| (空字串) | 略過本次輸入 |

### 單獨測試 Ollama 連線

```bash
python init_ollama.py
```

---

## Ollama API 細節

使用 Ollama 的 `/api/chat` 接口，messages 格式如下：

```python
[
    {"role": "system",    "content": "角色定義..."},
    {"role": "user",      "content": "使用者問題..."},
    {"role": "assistant", "content": "AI 回覆..."}
]
```

Request Payload：

```json
{
    "model": "qwen3:4b-instruct",
    "messages": [...],
    "stream": false
}
```

---

## 設定調整

- **模型**：於 `init_ollama.py` 修改 `self.model_name`
- **Ollama 主機 / Port**：於 `service.py` 實例化 `OllamaProvider(host=..., port=...)` 時傳入
- **System Prompt**：於 `service.py` 的 `self.system_prompt` 調整

---

## 未來擴充

- **FastAPI 封裝**：將 `Service.run()` 改為 Web Endpoint，提供給前端或行動端呼叫。
- **多人持久化儲存**：將 `ChatSession` 的資料從記憶體搬至 Redis，實現跨 process 的持久對話記憶。
- **Streaming 回應**：將 `stream` 改為 `True` 並以 SSE 傳回前端，改善長回覆的使用者體驗。
- **模型切換介面**：支援執行時動態切換模型。
