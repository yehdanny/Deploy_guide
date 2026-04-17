FROM python:3.10-slim

WORKDIR /app

# 複製 Audit 專用的依賴
COPY audit/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製 Audit 的程式碼
COPY audit/ .

# 執行 Audit Service，監聽 8000 埠
CMD ["uvicorn", "audit_log:app", "--host", "0.0.0.0", "--port", "8000"]