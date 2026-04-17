FROM python:3.10-slim

WORKDIR /app

# 複製並安裝依賴
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY app/ ./app/

# 預設執行 API (會被 docker-compose 的 command 覆蓋)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]