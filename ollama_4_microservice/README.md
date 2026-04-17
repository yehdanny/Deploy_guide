# 我的AI技能 - microservice 篇

### > 基本架構:
![alt text](image.png)

### > 套件
```python
from fastapi import FastAPI
import httpx
```

使用docker build、docker run、curl 測試


---

### 第一階段：容器化 [Containerization](C:\Users\ygz08\Work\Claude_vibe\place6\ollama_4_microservice\1_contatinerization\STEP.md)
微服務的基礎是容器。首先，練習將你的 API 程式碼撰寫成 Dockerfile。

練習建立一個簡單的 FastAPI 環境。

練習如何透過 docker-compose.yml 將 API 服務與 Ollama 連接起來（即便 Ollama 在宿主機執行）。

### 第二階段：異步解耦 [Decoupling](C:\Users\ygz08\Work\Claude_vibe\place6\ollama_4_microservice\2_Message_Queue\STEP.md)
這是微服務最關鍵的一環。AI 推論通常很慢，不應該讓使用者在 HTTP 請求上死等。

引進消息隊列 (Message Queue)： 練習使用 Redis 或 RabbitMQ。

流程： 1. 使用者發送請求到 API。
2. API 將任務丟入 Redis 隊列後立即回傳「任務 ID」。
3. Worker 服務從 Redis 抓取任務，呼叫 Ollama API，完成後將結果存入資料庫。

### 第三階段：服務發現與通訊 [Service Discovery and Communication](C:\Users\ygz08\Work\Claude_vibe\place6\ollama_4_microservice\3_Service_Discovery\STEP.md)
練習使用 HTTP 內網通訊：讓 API 服務透過容器名稱（如 http://ollama-worker:8000）而非 IP 地址與其他服務溝通。


### 進階挑戰
當你完成基礎連接後，可以嘗試以下進階練習：

動態擴展 (Scaling)： 嘗試啟動兩個 ai-worker 容器，觀察任務是否能被平均分配（負載平衡）。

健康檢查 (Health Check)： 寫一個腳本自動偵測 Ollama 是否在線，若斷線則讓 API 服務回傳「系統維護中」。

結構化輸出 (Structured Output)： 練習讓 Worker 服務強制要求 Ollama 回傳 JSON 格式，並由 API 服務解析驗證。

你想先從哪一個組件（API 或是 Docker 配置）開始撰寫程式碼呢？