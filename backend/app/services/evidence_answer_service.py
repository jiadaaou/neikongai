from app.services.embedding_service import embedding_service
from app.services.query_understanding_service import query_understanding_service
from app.core.database import get_db_connection
from app.ai_service import ai_service


class EvidenceAnswerService:
    """证据驱动回答服务（分层法律检索版）"""

    def answer_question(self, user_query: str):
        # 1. 用户问题理解
        query_profile = query_understanding_service.understand_query(user_query)
        retrieval_query = query_profile.get("retrieval_query") or user_query
        query_keywords = query_profile.get("keywords") or []
        query_objects = query_profile.get("objects") or []
        query_behavior = query_profile.get("behavior") or ""

        # 2. 向量化查询
        query_embedding = embedding_service.get_single_embedding(retrieval_query)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            candidates = []
            layer_results = {"5": [], "4": [], "3": [], "2": [], "1": []}

            # 3A. 关键词直召（全层级）
            if query_keywords:
                keyword_conditions = []
                params = []
                for kw in query_keywords[:8]:
                    keyword_conditions.append("(lc.chunk_text ILIKE %s OR lc.keywords::text ILIKE %s)")
                    params.extend([f"%{kw}%", f"%{kw}%"])

                sql_keyword = f"""
                    SELECT
                        lc.id,
                        lc.chunk_text,
                        lc.article_start,
                        ld.title,
                        lc.keywords,
                        0.0 as similarity,
                        'keyword' as source_type,
                        ld.legal_level
                    FROM legal_chunks lc
                    JOIN legal_documents ld ON lc.document_id = ld.id
                    WHERE ld.status = 'active'
                      AND ({' OR '.join(keyword_conditions)})
                    LIMIT 50
                """
                cursor.execute(sql_keyword, params)
                candidates.extend(cursor.fetchall())

            # 3B. 分层向量召回：每层各取前5
            for legal_level in [5, 4, 3, 2, 1]:
                cursor.execute("""
                    SELECT
                        lc.id,
                        lc.chunk_text,
                        lc.article_start,
                        ld.title,
                        lc.keywords,
                        1 - (lc.embedding <=> %s::vector) as similarity,
                        'vector' as source_type,
                        ld.legal_level
                    FROM legal_chunks lc
                    JOIN legal_documents ld ON lc.document_id = ld.id
                    WHERE ld.status = 'active'
                      AND ld.legal_level = %s
                    ORDER BY lc.embedding <=> %s::vector
                    LIMIT 5
                """, (query_embedding, legal_level, query_embedding))
                rows = cursor.fetchall()
                candidates.extend(rows)

        finally:
            cursor.close()
            conn.close()

        # 4. 合并去重（同一 chunk 只保留一份）
        merged = {}
        for row in candidates:
            chunk_id = row[0]
            chunk_text = row[1] or ""
            article_start = row[2]
            law_title = row[3]
            chunk_keywords = row[4] or []
            similarity = float(row[5]) if row[5] is not None else 0.0
            source_type = row[6]
            legal_level = int(row[7]) if row[7] is not None else 0

            base_score = similarity

            # 关键词直召基础加权
            if source_type == "keyword":
                base_score += 0.35

            # 法律层级权重（高层级略高）
            level_weight = {
                5: 0.12,
                4: 0.10,
                3: 0.08,
                2: 0.06,
                1: 0.04
            }.get(legal_level, 0.0)
            base_score += level_weight

            if chunk_id not in merged or base_score > merged[chunk_id]["base_score"]:
                merged[chunk_id] = {
                    "chunk_id": chunk_id,
                    "law_title": law_title,
                    "article_start": article_start,
                    "keywords": chunk_keywords,
                    "similarity": similarity,
                    "source_type": source_type,
                    "legal_level": legal_level,
                    "base_score": base_score,
                    "chunk_text": chunk_text,
                }

        # 5. 二次重排
        reranked = []
        for item in merged.values():
            chunk_text = item["chunk_text"]
            chunk_keywords = item["keywords"]
            score = item["base_score"]

            # 关键词命中加权
            for kw in query_keywords:
                if kw and (kw in chunk_text or kw in chunk_keywords):
                    score += 0.18

            # 对象命中加权
            for obj in query_objects:
                if obj and obj in chunk_text:
                    score += 0.12

            # 行为命中加权
            if query_behavior and query_behavior in chunk_text:
                score += 0.20

            # 行为 + 对象直接回答句加权
            for obj in query_objects:
                if query_behavior and obj:
                    if f"{query_behavior}{obj}" in chunk_text or f"{query_behavior} {obj}" in chunk_text:
                        score += 0.45

            # “必须/应当/依法 + 行为 + 对象”强加权
            direct_patterns = []
            for obj in query_objects:
                if query_behavior and obj:
                    direct_patterns.extend([
                        f"必须{query_behavior}{obj}",
                        f"应当{query_behavior}{obj}",
                        f"依法{query_behavior}{obj}",
                    ])
            for pattern in direct_patterns:
                if pattern in chunk_text:
                    score += 0.60

            # 法定义务句加权
            duty_markers = ["必须", "应当", "不得", "禁止", "依法", "应"]
            for marker in duty_markers:
                if marker in chunk_text:
                    score += 0.05

            # 合规判断类问题，优先义务条文
            if query_profile.get("question_type") in ["是否合法判断", "合规咨询"]:
                if "必须" in chunk_text or "应当" in chunk_text:
                    score += 0.10

            item["rerank_score"] = score
            reranked.append(item)

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)

        # 6. 生成每层级结果
        for item in reranked:
            level_key = str(item["legal_level"])
            if level_key in layer_results and len(layer_results[level_key]) < 3:
                layer_results[level_key].append(item)

        # 7. 最终取总 Top3 用于回答
        top_evidence = reranked[:3]

        evidence_text_parts = []
        for item in top_evidence:
            evidence_text_parts.append(
                f"{item['law_title']} {item['article_start']}：{item['chunk_text']}"
            )

        evidence_text = "\n\n".join(evidence_text_parts)

        if not evidence_text.strip():
            return {
                "question": user_query,
                "answer": "未检索到可用法律依据，暂时无法生成合规回答。",
                "evidence": [],
                "layer_results": layer_results,
                "query_profile": query_profile
            }

        prompt = f"""你是企业依法合规助手。

用户问题：
{user_query}

系统已检索到以下法律依据：
{evidence_text}

请严格遵守以下要求：
1. 只能基于以上法律依据回答，不得编造未提供的法律内容。
2. 回答必须明确引用法律名称和条文编号。
3. 先给结论，再给依据。
4. 如果现有证据不足以支持完整结论，必须明确说明“根据当前检索到的法条，证据仍有限”。
5. 语言保持专业、简洁、清晰。
"""

        answer = ai_service.chat([], prompt)

        return {
            "question": user_query,
            "answer": answer,
            "evidence": top_evidence,
            "layer_results": layer_results,
            "query_profile": query_profile
        }


evidence_answer_service = EvidenceAnswerService()
