# 我的AI技能 - deploy ollama 篇

---

透過 Ollama 本地 API 進行串流推理的簡易 Python 腳本。

## 功能

- 連接本地 Ollama 服務（預設 `http://127.0.0.1:11434`）
- 使用 `qwen3.5:35b-a3b` 模型
- 支援串流（streaming）輸出，逐字即時顯示回應

## 前置需求

- Python 3.12+
- [Ollama](https://ollama.com/) 已安裝並在本地執行
- 已拉取對應模型：
  ```bash
  ollama pull qwen3.5:35b-a3b
  ```

## 安裝

```bash
pip install -r requirements.txt
```

## 使用方式

```bash
python main.py
```

預設會向模型提問「解釋一下 Transformer」，並將回應串流印出至終端機。

若要修改提問內容，編輯 `main.py` 底部的 `ask_stream(...)` 呼叫即可。
