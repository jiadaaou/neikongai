from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.core.database import get_db_connection
from app.schemas import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse
from app.routers.auth import get_current_user
from app.ai_service import ai_service
from datetime import datetime

router = APIRouter()

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: dict = Depends(get_current_user)
):
    """创建新对话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        now = datetime.now()
        
        # 使用 SERIAL 自增 ID，不手动指定 id
        cursor.execute("""
            INSERT INTO conversations (user_id, title, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id, user_id, title, created_at, updated_at
        """, (int(current_user['id']), conversation.title, now, now))
        
        result = cursor.fetchone()
        conn.commit()
        
        return ConversationResponse(
            id=result[0],
            user_id=result[1],
            title=result[2],
            created_at=result[3],
            updated_at=result[4]
        )
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"创建对话失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: dict = Depends(get_current_user)
):
    """获取用户的所有对话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, user_id, title, created_at, updated_at
            FROM conversations
            WHERE user_id = %s
            ORDER BY updated_at DESC
        """, (int(current_user['id']),))
        
        results = cursor.fetchall()
        
        return [
            ConversationResponse(
                id=row[0],
                user_id=row[1],
                title=row[2],
                created_at=row[3],
                updated_at=row[4]
            )
            for row in results
        ]
    finally:
        cursor.close()
        conn.close()

@router.post("/messages", response_model=dict)
async def send_message(
    message: MessageCreate,
    current_user: dict = Depends(get_current_user)
):
    """发送消息并获取 AI 回复"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 验证对话是否属于当前用户
        cursor.execute("""
            SELECT id FROM conversations 
            WHERE id = %s AND user_id = %s
        """, (message.conversation_id, int(current_user['id'])))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="对话不存在")
        
        # 保存用户消息（使用自增 ID）
        now = datetime.now()
        
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (message.conversation_id, 'user', message.content, now))
        
        user_msg_id = cursor.fetchone()[0]
        
        # 获取历史消息（不包括刚插入的用户消息）
        cursor.execute("""
            SELECT role, content FROM messages
            WHERE conversation_id = %s AND id < %s
            ORDER BY created_at ASC
        """, (message.conversation_id, user_msg_id))
        
        history = cursor.fetchall()
        messages = [{"role": row[0], "content": row[1]} for row in history]
        
        # 调用 AI 服务（传递历史消息和当前用户消息）
        ai_response = ai_service.chat(messages, message.content)
        
        # 保存 AI 回复
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (message.conversation_id, 'assistant', ai_response, now))
        
        ai_msg_id = cursor.fetchone()[0]
        
        # 更新对话的 updated_at
        cursor.execute("""
            UPDATE conversations 
            SET updated_at = %s 
            WHERE id = %s
        """, (now, message.conversation_id))
        
        conn.commit()
        
        return {
            "user_message": {
                "id": user_msg_id,
                "role": "user",
                "content": message.content,
                "created_at": now.isoformat()
            },
            "ai_message": {
                "id": ai_msg_id,
                "role": "assistant",
                "content": ai_response,
                "created_at": now.isoformat()
            }
        }
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: int,
    current_user: dict = Depends(get_current_user)
):
    """获取对话的所有消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 验证对话是否属于当前用户
        cursor.execute("""
            SELECT id FROM conversations 
            WHERE id = %s AND user_id = %s
        """, (conversation_id, int(current_user['id'])))
        
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="对话不存在")
        
        # 获取消息
        cursor.execute("""
            SELECT id, conversation_id, role, content, created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC
        """, (conversation_id,))
        
        results = cursor.fetchall()
        
        return [
            MessageResponse(
                id=row[0],
                conversation_id=row[1],
                role=row[2],
                content=row[3],
                created_at=row[4]
            )
            for row in results
        ]
    finally:
        cursor.close()
        conn.close()
