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
既然你目前專注在**技術研發與架構優化**，我建議將這個練習分為四個「由內而外」的階段。

這樣的切分方式能讓你最直觀地感受 **Clean Architecture** 如何保護你的核心邏輯不受外部工具（如 Ollama 版本更新、API 變動）的影響。

---

### 第一階段：定義領域核心 [Domain Layer](./1_Domain_Layer/README.md)

<font color="orange">在這個階段，你甚至不需要安裝 `requests` 或 `ollama` 套件，只需構想需求、儲存的狀態。</font>

- 不寫任何實作邏輯

包含 :
    - 地基(models.py) : 會有一個Document和Summary。各自要包含什麼變數。
    - 藍圖(interfaces.py) : 會有一個summarize功能，輸入Document型別，輸出Summary型別。

---

### 第二階段：實作業務邏輯 [Use Case Layer](./2_UseCase_Layer/README.md)

<font color="orange">寫一個流程，讓藍圖可以運作。</font>

- 不寫任何實作邏輯

包含 :
    - 流程(use_cases/summarize_document.py) : 一個運行summarize的流程。

---

### 第三階段：對接外部工具 [Infrastructure Layer](./3_Infrastructure_Layer/README.md)

<font color="orange">將Ollama接入系統，並實作藍圖的介面。</font>

- 有實作邏輯
    - 用 工人+監工+執行 得到一個簡潔的可執行PIPELINE。
    - 覆蓋藍圖的功能。
---

### 第四階段：多樣化進入點 [App Layer](./4_APP_Layer/README.md)

<font color="orange">撰寫多個入口(CLI/FASTAPI)來驅動核心邏輯。</font>

- 這是最有趣的一步。因為你的核心邏輯 (Use Case) 已經穩定了，你可以輕易地為它穿上不同的「衣服」。
    - CLI 介面：寫一個簡單的 `main.py`，透過終端機輸入文字。
    - API 介面：用 **FastAPI** 封裝成一個 Service，供前端呼叫。
    - 成果：同一個 `TranslateUseCase` 同時驅動了 CLI 和 Web API，證明核心邏輯不需要為了不同的呈現方式而修改。

---
