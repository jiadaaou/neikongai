from fastapi import APIRouter
from pydantic import BaseModel
from app.services.evidence_answer_service import evidence_answer_service

router = APIRouter(prefix="/ai", tags=["AI-Answer"])


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask_ai(req: AskRequest):
    """
    AI合规问答接口
    """
    result = evidence_answer_service.answer_question(req.question)
    return {
        "success": True,
        "data": result
    }
