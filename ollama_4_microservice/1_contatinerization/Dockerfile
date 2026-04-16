# 1. 使用輕量級 Python 映像檔
FROM python:3.10-slim

# 2. 設定容器內的工作目錄
WORKDIR /app

# 3. 複製套件清單並安裝
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 複製所有程式碼到容器
COPY app/ ./app

# 5. 開放 8000 埠號
EXPOSE 8000

# 6. 執行 FastAPI (使用 uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]