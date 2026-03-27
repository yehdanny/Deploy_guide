# NotebookLM AI Podcast Pipeline

自動化 CNBC AI 新聞 → 繁中雙人 Podcast 影片 → YouTube 上傳

## Pipeline 流程

1. **CNBC 爬蟲** — 撈取當天 AI 文章
2. **NotebookLM** — 瀏覽器自動化生成繁中短版雙人 podcast
3. **音訊分離** — 拆分兩位主持人音軌
4. **SadTalker** — 生成 talking head 影片
5. **FFmpeg 合成** — 主講者切換 + PIP 佈局
6. **Thumbnail** — 模板 + 日期/主題
7. **YouTube 上傳** — Data API v3

## 設置

```bash
# 建立虛擬環境
python -m venv .venv
.venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
playwright install chromium

# 放置必要檔案
# - assets/speaker_a.png (Speaker A 大頭照)
# - assets/speaker_b.png (Speaker B 大頭照)
# - assets/thumbnail_template.png (Thumbnail 模板)
# - client_secrets.json (YouTube OAuth)
```

## 使用

```bash
# 首次：手動登入 NotebookLM
python step2_notebooklm.py --login

# 首次：YouTube OAuth
python step7_youtube_upload.py

# 跑完整 pipeline
python run_pipeline.py

# 跳過 NotebookLM（用現有音檔）
python run_pipeline.py --skip-notebooklm

# 指定第 N 篇文章（0-based）
python run_pipeline.py 2
```
