# 我的AI技能 - clean architecture 篇

## 1. 核心概念：分層設計
在 Clean Architecture 中，我們會由內而外分為四層。練習的重點在於：內層不應該知道外層的細節。層級名稱在本練習中的角色

|層級|名稱|在本練習中的角色|
|---|---|---|
|內層(1)| Entities (實體)|定義最基本的資料結構（例如：TranslationTask）。|
|內層(2)| Use Cases (案例)|負責翻譯的邏輯流（例如：檢查文字內容 -> 呼叫翻譯介面 -> 格式化輸出）。|
|外層(3)| Gateways / Adaptors|這裡定義「介面」(Interface)，規定 AI 模型該長怎樣，但不寫實作。|
|最外層(4)| Infrastructure / Frameworks|這裡才是 Ollama 實作的地方。 負責發送請求給 localhost:11434。|

## 2. 實作流程
1. 第一步：定義 Domain (Domain Layer)
先不要管 Ollama。定義你的「翻譯任務」和「AI 服務介面」。
第二步：撰寫 Use Case
Use Case 只依賴於上面的介面，它不知道背後是 Ollama 還是 ChatGPT。
第三步：實作 Infrastructure (Ollama)
這時候才引入 Ollama 的實作。

## 原因: 

### 為什麼這樣練習有效？
這份練習能讓你體會到三個關鍵好處：

- 可替換性：如果你明天想把 Ollama 換成 Qwen-2.5 或是 Llama-3，你只需要在 infrastructure 層寫一個新的 Class，完全不用動到 Use Case 裡的翻譯邏輯。
- 易於測試：你可以寫一個 MockAIService 來測試 Use Case，而不需要真的啟動 Ollama 模型（省下推論時間與記憶體）。
- 依賴反轉 (DIP)：Use Case 依賴的是抽象的 AIServiceInterface，而外層的 OllamaService 也要去符合內層定義的規則。

## 4. 進階練習建議
當你完成基礎架構後，可以試著加入以下功能：

- 加入 Repository 層：將翻譯過的紀錄存入 SQLite 或是 JSON 檔案。
- 加入 Input Validation：在 Entity 層檢查輸入字串是否為空。
- 更換進入點：分別寫一個 main.py (CLI 介面) 和一個 api.py (FastAPI 介面)，它們都呼叫同一個 TranslateTextUseCase。