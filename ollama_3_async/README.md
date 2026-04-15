# 我的AI技能 - async / concurrency 篇

---


階段一：基礎非同步實作 (Basic Async)
環境建置： 學習如何安裝並使用非同步版本的 Client 端庫（如 ollama.AsyncClient）。

定義協程 (Coroutine)： 使用 async def 定義一個封裝 Ollama 請求的函式，並理解 await 的放置位置。

單一非同步呼叫： 練習在不阻塞主線程的情況下，發送一次請求並獲取結果。

階段二：並發執行與效能對比 (Concurrency & Benchmarking)
多任務排程： 學習將多個模型請求打包成一個任務列表。

使用 asyncio.gather： 實作同時發送多個請求，並觀察程式如何「同時」啟動多個任務。

時間效能分析： 計算「並發執行」與「傳統迴圈同步執行」的總耗時差異，理解非同步在 I/O 等待時的優勢。

階段三：資源管理與流程控制 (Flow Control)
並發限流 (Semaphore)：

學習使用 asyncio.Semaphore。

目標： 限制同時執行的 Ollama 任務數量（例如一次只跑 2 個），避免 VRAM 溢出或硬體過負載。

串流處理 (Streaming)： 實作 async for 迭代器，練習如何在模型生成的過程中即時輸出字元（Token），而非等待整段生成完畢。

超時管理 (Timeout)： 使用 asyncio.wait_for 為模型回應設定上限時間，防止某個請求卡死導致整個程式停滯。

階段四：進階錯誤處理 (Error Handling)
例外擷取： 練習在非同步環境中處理連線中斷或模型未啟動的錯誤。

部分成功處理： 練習當 5 個並發任務中有 1 個失敗時，如何確保其他 4 個結果仍能正常被接收與處理。

階段五：實際應用模擬 (Real-world Scenario)
Pipeline 實作： 模擬一個 AI 代理人工作流，例如：同時請模型「總結摘要」與「提取關鍵字」，並將這兩個並發任務的結果整合輸出。