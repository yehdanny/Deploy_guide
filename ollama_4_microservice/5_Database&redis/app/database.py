from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import datetime
import os
import time
from sqlalchemy.exc import OperationalError

load_dotenv()
user = os.getenv("POSTGRES_USER")
print(f"--- ATTEMPTING TO CONNECT WITH USER: {user} ---")

SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 定義儲存 AI 結果的資料表結構
class AIResult(Base):
    __tablename__ = "results"
    task_id = Column(String, primary_key=True, index=True)
    prompt = Column(Text)
    model = Column(String)
    answer = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# 初始化資料庫（建立資料表）
def init_db():
    retries = 5
    while retries > 0:
        try:
            # 嘗試建立資料表
            Base.metadata.create_all(bind=engine)
            print("--- 資料庫連線成功並初始化完成！ ---")
            break
        except OperationalError as e:
            retries -= 1
            print(f"--- 資料庫尚未就緒，等待中... (剩餘重試次數: {retries}) ---")
            time.sleep(3)  # 等 3 秒再試一次

    if retries == 0:
        print("--- 無法連線至資料庫，請檢查 Docker 狀態 ---")
        raise Exception("Database connection failed")


init_db()
