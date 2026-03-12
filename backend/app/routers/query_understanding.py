from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.query_understanding_service import query_understanding_service


router = APIRouter(prefix="/ai", tags=["AI-Query-Understanding"])


class QueryUnderstandRequest(BaseModel):
    user_query: str
    company_context: Optional[Dict[str, Any]] = None


@router.post("/query-understand")
async def query_understand(payload: QueryUnderstandRequest):
    result = query_understanding_service.understand_query(
        user_query=payload.user_query,
        company_context=payload.company_context or {}
    )
    return {
        "success": True,
        "data": result
    }
