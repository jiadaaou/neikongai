from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db_connection
from app.routers.auth import oauth2_scheme
from jose import jwt
import os

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的token")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="无效的token")

@router.get("/profile", response_model=UserProfile)
async def get_profile(user_id: str = Depends(get_current_user_id)):
    """获取用户资料"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return {
            "id": str(user[0]),
            "username": user[1],
            "email": user[2],
            "created_at": user[3]
        }
    finally:
        cursor.close()
        conn.close()
