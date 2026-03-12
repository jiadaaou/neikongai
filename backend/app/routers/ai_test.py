from fastapi import APIRouter
from app.ai_service import ai_service

router = APIRouter()

@router.get("/ai/test")
async def test_ai():
    """测试通义千问 API 连接"""
    is_connected = ai_service.test_connection()
    
    if is_connected:
        # 测试简单对话
        response = ai_service.chat([], "你好，请简单介绍一下劳动法")
        return {
            "status": "success",
            "message": "通义千问 API 连接成功",
            "test_response": response
        }
    else:
        return {
            "status": "error",
            "message": "通义千问 API 连接失败"
        }
