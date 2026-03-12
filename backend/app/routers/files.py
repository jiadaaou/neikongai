from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.routers.auth import oauth2_scheme
from jose import jwt
import os

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的token")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="无效的token")

class FileResponse(BaseModel):
    id: str
    filename: str
    size: int
    upload_date: datetime

@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """上传文件（暂未实现完整功能）"""
    return {
        "id": "temp-id",
        "filename": file.filename,
        "size": 0,
        "upload_date": datetime.utcnow()
    }

@router.get("/", response_model=List[FileResponse])
async def list_files(user_id: str = Depends(get_current_user_id)):
    """获取文件列表（暂未实现完整功能）"""
    return []
