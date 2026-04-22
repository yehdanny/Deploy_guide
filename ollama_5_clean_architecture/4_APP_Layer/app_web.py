# app_web.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from infrastructure.ollama_adapter import OllamaSummarizer
from use_cases.summarize_document import SummarizeDocumentUseCase

app = FastAPI()

# 1. 在啟動時完成組裝
real_ai = OllamaSummarizer(model_name="qwen3:4b-instruct-2507-fp16")
summarizer_app = SummarizeDocumentUseCase(ai_service=real_ai)


class RequestBody(BaseModel):
    text: str
    source: str = "Web_API"


@app.post("/summarize")
async def summarize_endpoint(body: RequestBody):
    # 2. 直接呼叫 Use Case
    try:
        result = summarizer_app.execute(text=body.text, source=body.source)
        return {
            "summary": result.raw_text,
            "length": result.word_count,
            "engine": result.model_name,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 啟動命令: uv run uvicorn app_web:app --reload
