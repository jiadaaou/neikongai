import os
import sys
from pathlib import Path

env_path = Path("/var/www/neikongai/backend/.env")
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

sys.path.insert(0, "/var/www/neikongai/backend")

from app.services.embedding_service import embedding_service
from app.core.database import get_db_connection

question = "某企业为了提高外界对企业经营状况的评价，在对外沟通和资料提供过程中，有意让外部机构形成与真实经营情况不同的认识。企业内部人员按照管理层统一安排准备相关材料。如果这些资料被用于商业合作或金融机构决策，这种行为在法律上是否存在风险？"

print("=" * 100)
print("测试问题：", question)
print("说明：本次测试不告诉系统任何法律名称，直接在全部法律文档中检索。")
print("=" * 100)

query_embedding = embedding_service.get_embeddings([question])[0]
if not query_embedding:
    raise Exception("问题向量化失败")

conn = get_db_connection()
cur = conn.cursor()

cur.execute("""
    SELECT
        d.id AS document_id,
        d.title,
        c.chunk_index,
        c.article_start,
        c.article_end,
        LEFT(c.chunk_text, 220) AS preview,
        c.embedding <=> %s::vector AS distance
    FROM legal_chunks c
    JOIN legal_documents d ON d.id = c.document_id
    WHERE d.processed_status = 'completed'
    ORDER BY c.embedding <=> %s::vector
    LIMIT 12
""", (query_embedding, query_embedding))

rows = cur.fetchall()

print("\nTop 12 相似法条：")
for row in rows:
    document_id, title, chunk_index, article_start, article_end, preview, distance = row
    print("-" * 100)
    print(f"document_id : {document_id}")
    print(f"title       : {title}")
    print(f"chunk_index : {chunk_index}")
    print(f"article     : {article_start} ~ {article_end}")
    print(f"distance    : {distance}")
    print(f"preview     : {preview}")

cur.close()
conn.close()

print("\n测试完成。")
