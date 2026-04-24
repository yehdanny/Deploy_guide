# domain/ingredient.py
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
from uuid import uuid4


@dataclass(frozen=True)
class User_input:
    content: str
    user_id: str
    trace_id: str = "" #訂單編號


@dataclass(frozen=True)
class IntentType(Enum):
    QUERY_FAQ = "query_faq"
    GET_ORDER = "get_order"
    GENERAL_CHAT = "general_chat"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class IntentAnalysis:
    """Agent 對使用者意圖的分析結果"""

    primary_intent: IntentType
    confidence: float
    extracted_entities: Dict[str, Any]  # 例如 {"order_id": "ORD-12345"}
    raw_reasoning: str  # 儲存 AI 的思考過程 (Chain of Thought)


@dataclass(frozen=True)
class ToolResult:
    """所有工具輸出的統一包裝"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    source_system: str = "unknown"  # 'query_faq', 'get_order', 'general_chat'


@dataclass(frozen=True)
class CustomerResponse:
    """最終回傳給前端的資料結構"""

    content: str
    sources: List[str]  # ["FAQ 知識庫", "物流 API (2024-05-19)"]
    suggested_actions: List[str] = field(
        default_factory=list
    )  # ["退貨申請", "聯繫真人"]
    trace_id: str = ""  # 用於 debug 整個 agent workflow
