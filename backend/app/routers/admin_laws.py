"""
管理员法律文档路由
提供法律文档的上传、管理、查询等 API
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from app.core.database import get_db_connection
from app.services.document_processor import doc_processor
from app.services.embedding_service import embedding_service
from app.services.query_understanding_service import query_understanding_service
import os
import hashlib
import shutil
from datetime import datetime
from typing import Optional
import asyncio
from app.routers.auth import get_current_user as require_admin


router = APIRouter(prefix="/admin/laws", tags=["Admin-Laws"])


# 文件上传目录
UPLOAD_DIR = "/var/www/neikongai/uploads/laws"
os.makedirs(UPLOAD_DIR, exist_ok=True)





@router.post("/upload")
async def upload_law(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    legal_level: int = Form(...),
    doc_number: Optional[str] = Form(None),
    effective_date: Optional[str] = Form(None),
    # current_user: dict = Depends(require_admin)  # 开发阶段禁用
):
    """
    上传法律文档并自动处理
    
    Args:
        file: 文件（PDF/Word/TXT）
        title: 法律名称
        legal_level: 法律层级（1-5）
        doc_number: 文号（可选）
        effective_date: 生效日期（可选）
    
    Returns:
        {
            "success": True,
            "document_id": 123,
            "message": "文档上传成功，正在后台处理..."
        }
    """
    try:
        # 验证文件格式
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}. 支持的格式: {allowed_extensions}"
            )
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 计算文件哈希
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # 插入数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO legal_documents (
                    title,
                    legal_level,
                    doc_number,
                    effective_date,
                    original_filename,
                    file_path,
                    file_hash,
                    full_text,
                    processed_status,
                    uploaded_by,
                    uploaded_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id
            """, (
                title,
                legal_level,
                doc_number,
                effective_date,
                file.filename,
                file_path,
                file_hash,
                "",  # 暂时为空，处理时会填充
                "pending",
                1  # TODO: 使用真实用户ID
            ))
            
            document_id = cursor.fetchone()[0]
            conn.commit()
            
            # 添加后台任务：异步处理文档
            background_tasks.add_task(process_document_task, document_id, file_path)
            
            return {
                "success": True,
                "document_id": document_id,
                "message": "文档上传成功，正在后台处理..."
            }
            
        except Exception as e:
            conn.rollback()
            # 删除已上传的文件
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")
        finally:
            cursor.close()
            conn.close()
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


async def process_document_task(document_id: int, file_path: str):
    """后台任务：处理文档"""
    try:
        # 更新状态为处理中
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE legal_documents SET processed_status = %s WHERE id = %s",
            ("processing", document_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        # 调用处理器
        result = await doc_processor.process_document(document_id, file_path)
        
        print(f"✅ 文档 {document_id} 处理完成: {result}")
        
    except Exception as e:
        print(f"❌ 文档 {document_id} 处理失败: {str(e)}")


@router.get("")
async def get_laws(
    legal_level: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
    # current_user: dict = Depends(require_admin)  # 开发阶段禁用
):
    """
    获取法律文档列表（分页、筛选）
    
    Args:
        legal_level: 法律层级筛选
        status: 状态筛选
        search: 搜索关键词
        page: 页码
        per_page: 每页数量
    
    Returns:
        {
            "data": [...],
            "total": 100,
            "page": 1,
            "per_page": 20
        }
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 构建查询条件
        conditions = []
        params = []
        
        if legal_level:
            conditions.append("legal_level = %s")
            params.append(legal_level)
        
        if status:
            conditions.append("status = %s")
            params.append(status)
        
        if search:
            conditions.append("title ILIKE %s")
            params.append(f"%{search}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 查询总数
        cursor.execute(f"SELECT COUNT(*) FROM legal_documents WHERE {where_clause}", params)
        total = cursor.fetchone()[0]
        
        # 查询数据
        offset = (page - 1) * per_page
        params.extend([per_page, offset])
        
        cursor.execute(f"""
            SELECT 
                id, title, legal_level, doc_number, effective_date,
                status, processed_status, chunks_count, uploaded_at,
                CASE legal_level
                    WHEN 5 THEN '宪法'
                    WHEN 4 THEN '法律'
                    WHEN 3 THEN '行政法规'
                    WHEN 2 THEN '部门规章'
                    WHEN 1 THEN '地方法规'
                END as legal_level_name
            FROM legal_documents
            WHERE {where_clause}
            ORDER BY uploaded_at DESC
            LIMIT %s OFFSET %s
        """, params)
        
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return {
            "data": data,
            "total": total,
            "page": page,
            "per_page": per_page
        }
        
    finally:
        cursor.close()
        conn.close()


@router.get("/{document_id}")
async def get_law_detail(
    document_id: int,
    # current_user: dict = Depends(require_admin)  # 开发阶段禁用
):
    """获取法律文档详情"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                id, title, legal_level, doc_number, effective_date,
                status, original_filename, file_path, processed_status,
                chunks_count, uploaded_at, structure_json,
                CASE legal_level
                    WHEN 5 THEN '宪法'
                    WHEN 4 THEN '法律'
                    WHEN 3 THEN '行政法规'
                    WHEN 2 THEN '部门规章'
                    WHEN 1 THEN '地方法规'
                END as legal_level_name
            FROM legal_documents
            WHERE id = %s
        """, (document_id,))
        
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        columns = [desc[0] for desc in cursor.description]
        data = dict(zip(columns, row))
        
        return data
        
    finally:
        cursor.close()
        conn.close()


@router.get("/{document_id}/chunks")
async def get_chunks(
    document_id: int,
    # current_user: dict = Depends(require_admin)  # 开发阶段禁用
):
    """获取文档的分块列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                id, chunk_index, chunk_text, chunk_type,
                chapter_number, chapter_title,
                section_number, section_title,
                article_start, article_end, articles_included,
                keywords, cited_count
            FROM legal_chunks
            WHERE document_id = %s
            ORDER BY chunk_index
        """, (document_id,))
        
        columns = [desc[0] for desc in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return {"chunks": data, "total": len(data)}
        
    finally:
        cursor.close()
        conn.close()


@router.get("/chunks/{chunk_id}")
async def get_chunk_detail(
    chunk_id: int,
    # current_user: dict = Depends(require_admin)  # 开发阶段禁用
):
    """获取分块详情"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                lc.*,
                ld.title as document_title,
                ld.legal_level_name
            FROM legal_chunks lc
            JOIN (
                SELECT id, title,
                    CASE legal_level
                        WHEN 5 THEN '宪法'
                        WHEN 4 THEN '法律'
                        WHEN 3 THEN '行政法规'
                        WHEN 2 THEN '部门规章'
                        WHEN 1 THEN '地方法规'
                    END as legal_level_name
                FROM legal_documents
            ) ld ON lc.document_id = ld.id
            WHERE lc.id = %s
        """, (chunk_id,))
        
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="分块不存在")
        
        columns = [desc[0] for desc in cursor.description]
        data = dict(zip(columns, row))
        
        # 移除 embedding 字段（太大）
        if 'embedding' in data:
            data['embedding'] = f"[向量维度: {len(data['embedding']) if data['embedding'] else 0}]"
        
        return data
        
    finally:
        cursor.close()
        conn.close()


@router.delete("/{document_id}")
async def delete_law(
    document_id: int,
    # current_user: dict = Depends(require_admin)  # 开发阶段禁用
):
    """删除法律文档（级联删除分块和日志）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取文件路径
        cursor.execute("SELECT file_path FROM legal_documents WHERE id = %s", (document_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        file_path = row[0]
        
        # 删除数据库记录（会级联删除分块和日志）
        cursor.execute("DELETE FROM legal_documents WHERE id = %s", (document_id,))
        conn.commit()
        
        # 删除文件
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        return {"success": True, "message": "删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.get("/{document_id}/logs")
async def get_processing_logs(
    document_id: int,
    # current_user: dict = Depends(require_admin)  # 开发阶段禁用
):
    """获取文档处理日志"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                id, step, status, details, processing_time_ms,
                error_message, created_at
            FROM document_processing_log
            WHERE document_id = %s
            ORDER BY created_at
        """, (document_id,))
        
        columns = [desc[0] for desc in cursor.description]
        logs = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return {"logs": logs}
        
    finally:
        cursor.close()
        conn.close()


@router.post("/test-search")
async def test_search(
    query: str = Form(...),
    top_k: int = Form(5),
    # current_user: dict = Depends(require_admin)  # 开发阶段禁用
):
    """
    测试混合检索：
    1. 用户问题理解
    2. 关键词命中
    3. 向量检索
    """
    try:
        query_profile = query_understanding_service.understand_query(query)
        retrieval_query = query_profile.get("retrieval_query") or query
        query_keywords = query_profile.get("keywords") or []

        query_embedding = embedding_service.get_single_embedding(retrieval_query)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                lc.id,
                lc.chunk_text,
                lc.article_start,
                lc.chapter_number,
                ld.title,
                lc.keywords,
                1 - (lc.embedding <=> %s::vector) as similarity,
                CASE
                    WHEN array_length(%s::text[], 1) IS NULL THEN 0
                    WHEN lc.keywords && %s::text[] THEN 1
                    ELSE 0
                END as keyword_hit
            FROM legal_chunks lc
            JOIN legal_documents ld ON lc.document_id = ld.id
            WHERE ld.status = 'active'
            ORDER BY keyword_hit DESC, lc.embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, query_keywords, query_keywords, query_embedding, top_k))

        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return {
            "query": query,
            "query_profile": query_profile,
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.put("/chunks/{chunk_id}")
async def update_chunk(
    chunk_id: int,
    chunk_text: str = Form(...),
    chapter_number: str = Form(None),
    article_start: str = Form(None),
    article_end: str = Form(None),
    # current_user: dict = Depends(require_admin)  # 开发阶段禁用
):
    """
    更新分块内容并重新向量化
    
    Args:
        chunk_id: 分块ID
        chunk_text: 新的文本内容
        chapter_number: 章节编号
        article_start: 起始条款
        article_end: 结束条款
    
    Returns:
        {"success": True, "message": "更新成功"}
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查分块是否存在
        cursor.execute("SELECT id FROM legal_chunks WHERE id = %s", (chunk_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="分块不存在")
        
        # 生成新的向量
        print(f"🔄 正在为分块 {chunk_id} 重新生成向量...")
        new_embedding = embedding_service.get_single_embedding(chunk_text)
        
        if not new_embedding:
            raise HTTPException(status_code=500, detail="向量生成失败")
        
        # 更新分块
        cursor.execute("""
            UPDATE legal_chunks
            SET 
                chunk_text = %s,
                chapter_number = %s,
                article_start = %s,
                article_end = %s,
                embedding = %s::vector
            WHERE id = %s
        """, (
            chunk_text,
            chapter_number,
            article_start,
            article_end,
            new_embedding,
            chunk_id
        ))
        
        conn.commit()
        
        print(f"✅ 分块 {chunk_id} 更新成功")
        
        return {
            "success": True,
            "message": "更新成功，已重新向量化"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.post("/{document_id}/reprocess")
async def reprocess_document(
    document_id: int,
    background_tasks: BackgroundTasks,
    # current_user: dict = Depends(require_admin)  # 开发阶段禁用
):
    """
    重新处理文档（删除旧分块，重新分块和向量化）
    
    Args:
        document_id: 文档ID
    
    Returns:
        {"success": True, "message": "已标记为待重新处理"}
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查文档是否存在
        cursor.execute(
            "SELECT id, file_path FROM legal_documents WHERE id = %s",
            (document_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        file_path = row[1]
        
        # 删除旧的分块
        cursor.execute("DELETE FROM legal_chunks WHERE document_id = %s", (document_id,))
        
        # 删除处理日志
        cursor.execute("DELETE FROM document_processing_log WHERE document_id = %s", (document_id,))
        
        # 更新文档状态
        cursor.execute("""
            UPDATE legal_documents
            SET 
                processed_status = 'pending',
                chunks_count = 0,
                full_text = '',
                structure_json = NULL
            WHERE id = %s
        """, (document_id,))
        
        conn.commit()
        
        # 添加后台任务重新处理
        background_tasks.add_task(process_document_task, document_id, file_path)
        
        print(f"🔄 文档 {document_id} 已标记为待重新处理")
        
        return {
            "success": True,
            "message": "文档已标记为待重新处理，请等待处理完成"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"操作失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@router.delete("/chunks/{chunk_id}")
async def delete_chunk(
    chunk_id: int,
    # current_user: dict = Depends(require_admin)  # 开发阶段禁用
):
    """
    删除分块
    
    Args:
        chunk_id: 分块ID
    
    Returns:
        {"success": True, "message": "删除成功"}
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查分块是否存在
        cursor.execute(
            "SELECT document_id FROM legal_chunks WHERE id = %s",
            (chunk_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="分块不存在")
        
        document_id = row[0]
        
        # 删除分块
        cursor.execute("DELETE FROM legal_chunks WHERE id = %s", (chunk_id,))
        
        # 更新文档的分块数量
        cursor.execute("""
            UPDATE legal_documents
            SET chunks_count = (
                SELECT COUNT(*) FROM legal_chunks WHERE document_id = %s
            )
            WHERE id = %s
        """, (document_id, document_id))
        
        conn.commit()
        
        print(f"🗑️  分块 {chunk_id} 已删除")
        
        return {
            "success": True,
            "message": "分块已删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()
