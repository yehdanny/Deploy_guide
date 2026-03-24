# 🎬 Animal Shorts — AI 動物對決 YouTube Shorts 自動生成

自動生成「自然環境中兩物種鬥爭」主題的 YouTube Shorts。

## 📊 專案狀態

| 項目 | 狀態 |
|------|------|
| Pipeline | ✅ 已跑通（2026-03-24） |
| 第一支影片 | ✅ [螳螂蝦 vs 螃蟹](https://youtube.com/shorts/W-xsE5YBGJs) |
| 影片生成 | Kling AI 網頁自動化（browser automation） |
| 影片上傳 | YouTube Data API v3 + OAuth2 |

## 🏗️ 架構

```
Step 1: 生成腳本        → 隨機選主題 + 生成 Kling prompt + YouTube 標題描述
Step 2: Kling 生成影片   → 瀏覽器自動化操作 app.klingai.com
Step 3: 加音效          → ffmpeg 加入動物聲 + 環境音（待完善）
Step 4: 上傳 YouTube    → YouTube Data API v3 自動上傳為 Short
```

## 📁 檔案結構

```
animal-shorts/
├── .venv/                      # Python 虛擬環境
├── config/
│   ├── client_secret.json      # Google OAuth 憑證
│   ├── token.json              # OAuth token（自動生成）
│   ├── kling_api.json          # Kling API key（目前未使用）
│   ├── kling_browser_profile/  # Kling 登入 session（Chromium profile）
│   ├── settings.json           # 影片設定（解析度、時長等）
│   └── .gitignore              # 防止敏感檔案被 commit
├── output/
│   ├── debug/                  # 截圖（除錯用）
│   ├── used_topics.json        # 已使用主題紀錄（避免重複）
│   └── YYYYMMDD_HHMMSS_xxx/    # 每次生成的 job 資料夾
│       ├── job.json            # 任務狀態 + metadata
│       ├── segment_1.mp4       # 影片片段
│       └── final_short.mp4     # 合併後的影片
├── topics.json                 # 30 組動物對決主題庫
├── requirements.txt            # Python 依賴
├── step1_generate_script.py    # Step 1: 生成腳本
├── step2_generate_video.py     # Step 2: Kling 影片生成（瀏覽器自動化）
├── step3_add_audio.py          # Step 3: 加音效
├── step4_upload_youtube.py     # Step 4: 上傳 YouTube
├── run_pipeline.py             # 一鍵執行全流程
├── kling_login.py              # Kling 登入（首次使用）
├── grab_video.py               # 影片下載工具
└── README.md                   # 本文件
```

## 🚀 使用方式

### 環境準備（首次）

```powershell
cd animal-shorts

# 啟動虛擬環境
.\.venv\Scripts\Activate.ps1

# 安裝依賴（已完成）
pip install -r requirements.txt
pip install PyJWT playwright
playwright install chromium
```

### 首次登入 Kling

```powershell
python kling_login.py
# 在跳出的瀏覽器中登入 Kling AI，登入後自動關閉
```

### 首次 YouTube 授權

首次執行 Step 4 時會自動跳出 Google OAuth 授權頁面，授權後 token 會存在 `config/token.json`。

### 執行 Pipeline

```powershell
# 設定環境變數（解決中文編碼問題）
$env:PYTHONIOENCODING='utf-8'

# Step 1: 生成腳本
python step1_generate_script.py
# 輸出 job 目錄路徑，例如: output/20260324_xxx_Lion_vs_Hyena

# Step 2: 生成影片（會開瀏覽器）
python step2_generate_video.py "output/20260324_xxx_Lion_vs_Hyena"

# Step 3: 加音效（需要 ffmpeg）
python step3_add_audio.py "output/20260324_xxx_Lion_vs_Hyena"

# Step 4: 上傳 YouTube
python step4_upload_youtube.py "output/20260324_xxx_Lion_vs_Hyena"
```

## 💰 費用

| 項目 | 費用 |
|------|------|
| Kling Standard Plan | $6.99/月（660 credits） |
| YouTube API | 免費 |
| 每支影片成本 | ~20 credits（舊版模型） |
| 每月可生成 | ~33 支影片 |

> ⚠️ VIDEO 3.0 Omni 每支要 60 credits，建議切換到 VIDEO 2.0 或更早版本省 credits。

## 🔧 待完善

- [ ] Step 2 偵測影片完成邏輯優化（改用 Kling 內部 API）
- [ ] Step 2 切換到便宜模型（VIDEO 2.0）
- [ ] Step 3 音效功能（需安裝 ffmpeg：`winget install ffmpeg`）
- [ ] 縮圖自動生成
- [ ] Windows Task Scheduler 每日自動排程
- [ ] Kling session 過期自動重新登入
- [ ] 錯誤重試機制

## 📝 主題庫

`topics.json` 包含 30 組對決主題，例如：
- 獅子 vs 鬣狗（非洲草原）
- 鱷魚 vs 河馬（非洲河流）
- 老鷹 vs 蛇（岩石懸崖）
- 虎鯨 vs 大白鯊（開放海域）
- 雪豹 vs 岩羊（喜馬拉雅山）
- ...等

系統會自動輪換主題，避免短期內重複。

## ⚠️ 注意事項

- Kling 登入 session 會過期，過期後需重新執行 `kling_login.py`
- YouTube OAuth token 會自動刷新，通常不需要重新授權
- 影片使用 Kling 網頁端 credits（非 API credits）
- `config/` 下的敏感檔案已加入 `.gitignore`
