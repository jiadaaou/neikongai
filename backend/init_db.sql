-- NeikongAI 数据库初始化脚本
-- 适用：PostgreSQL 14+，需要 pgvector 扩展
-- 用法：psql -U neikongai_user -d neikongai -f init_db.sql

-- ============================================================
-- 0. 扩展
-- ============================================================
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- 1. 用户表
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id                SERIAL          PRIMARY KEY,
    username          VARCHAR(50)     UNIQUE NOT NULL,
    email             VARCHAR(100)    UNIQUE NOT NULL,
    hashed_password   VARCHAR(200)    NOT NULL,
    full_name         VARCHAR(100),
    phone             VARCHAR(20),
    role              VARCHAR(30)     NOT NULL DEFAULT 'company_user',
                                      -- super_admin / company_admin / company_user
    company_id        INTEGER,
    is_active         BOOLEAN         NOT NULL DEFAULT TRUE,
    is_verified       BOOLEAN         NOT NULL DEFAULT FALSE,
    last_login        TIMESTAMPTZ,
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ
);

-- ============================================================
-- 2. 企业表（预留，用于多租户扩展）
-- ============================================================
CREATE TABLE IF NOT EXISTS companies (
    id                SERIAL          PRIMARY KEY,
    name              VARCHAR(200)    UNIQUE NOT NULL,
    code              VARCHAR(50)     UNIQUE NOT NULL,
    contact_name      VARCHAR(100),
    contact_email     VARCHAR(100),
    contact_phone     VARCHAR(20),
    is_active         BOOLEAN         NOT NULL DEFAULT TRUE,
    storage_quota     BIGINT          NOT NULL DEFAULT 10737418240,  -- 10 GB
    storage_used      BIGINT          NOT NULL DEFAULT 0,
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ
);

-- ============================================================
-- 3. 法律 / 行业准则文档表
-- （法律和行业准则共用同一张表，通过 legal_level 区分）
-- legal_level 含义：
--   5 = 宪法   4 = 法律   3 = 行政法规
--   2 = 部门规章   1 = 地方法规
--   0 = 行业准则（standards）
-- ============================================================
CREATE TABLE IF NOT EXISTS legal_documents (
    id                SERIAL          PRIMARY KEY,
    title             VARCHAR(500)    NOT NULL,
    legal_level       INTEGER         NOT NULL DEFAULT 4,
    doc_number        VARCHAR(200),
    effective_date    VARCHAR(50),
    original_filename VARCHAR(500)    NOT NULL,
    file_path         VARCHAR(1000)   NOT NULL,
    file_hash         VARCHAR(64),
    full_text         TEXT,
    structure_json    JSONB,
    processed_status  VARCHAR(30)     NOT NULL DEFAULT 'pending',
                                      -- pending / processing / completed / failed
    status            VARCHAR(30)     NOT NULL DEFAULT 'active',
                                      -- active / archived / deleted
    chunks_count      INTEGER         NOT NULL DEFAULT 0,
    uploaded_by       INTEGER         REFERENCES users(id) ON DELETE SET NULL,
    uploaded_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ
);

-- ============================================================
-- 4. 法律 / 行业准则文档分块表（含向量）
-- ============================================================
CREATE TABLE IF NOT EXISTS legal_chunks (
    id                SERIAL          PRIMARY KEY,
    document_id       INTEGER         NOT NULL REFERENCES legal_documents(id) ON DELETE CASCADE,
    legal_level       INTEGER         NOT NULL DEFAULT 4,
    chunk_index       INTEGER         NOT NULL,
    chunk_text        TEXT            NOT NULL,
    chunk_hash        VARCHAR(64),
    chunk_type        VARCHAR(50),
    chapter_number    VARCHAR(20),
    chapter_title     VARCHAR(500),
    section_number    VARCHAR(20),
    section_title     VARCHAR(500),
    article_start     VARCHAR(50),
    article_end       VARCHAR(50),
    articles_included JSONB,
    has_references    BOOLEAN         NOT NULL DEFAULT FALSE,
    reference_articles JSONB,
    expanded_text     TEXT,
    keywords          JSONB,
    articles_detail   JSONB,
    articles_count    INTEGER         NOT NULL DEFAULT 0,
    embedding         vector(1536),
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- 向量相似度检索索引（HNSW，生产环境推荐）
CREATE INDEX IF NOT EXISTS legal_chunks_embedding_idx
    ON legal_chunks USING hnsw (embedding vector_cosine_ops);

-- 文档 ID 普通索引（加速按文档查分块）
CREATE INDEX IF NOT EXISTS legal_chunks_document_id_idx
    ON legal_chunks (document_id);

-- ============================================================
-- 5. AI 合规分析单元表（一分块一条记录）
-- ============================================================
CREATE TABLE IF NOT EXISTS ai_law_units (
    id                SERIAL          PRIMARY KEY,
    chunk_id          INTEGER         UNIQUE NOT NULL REFERENCES legal_chunks(id) ON DELETE CASCADE,
    document_id       INTEGER         NOT NULL REFERENCES legal_documents(id) ON DELETE CASCADE,
    source_article    VARCHAR(100),
    subject           TEXT,
    behavior          TEXT,
    obligation        TEXT,
    prohibition       TEXT,
    risk_type         VARCHAR(100),
    risk_level        VARCHAR(20),
    compliance_action TEXT,
    keywords          JSONB,
    analysis_model    VARCHAR(100),
    analysis_status   VARCHAR(30),
    raw_ai_output     JSONB,
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ
);

-- ============================================================
-- 6. 文档处理日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS document_processing_log (
    id                SERIAL          PRIMARY KEY,
    document_id       INTEGER         NOT NULL REFERENCES legal_documents(id) ON DELETE CASCADE,
    step              VARCHAR(100)    NOT NULL,
    status            VARCHAR(30)     NOT NULL,   -- processing / success / failed
    details           JSONB,
    processing_time_ms INTEGER,
    error_message     TEXT,
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 7. 对话表（企业用户 AI 问答历史）
-- ============================================================
CREATE TABLE IF NOT EXISTS conversations (
    id                SERIAL          PRIMARY KEY,
    user_id           INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title             VARCHAR(500)    NOT NULL DEFAULT '新对话',
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 8. 消息表（对话内的单条消息）
-- ============================================================
CREATE TABLE IF NOT EXISTS messages (
    id                SERIAL          PRIMARY KEY,
    conversation_id   INTEGER         NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role              VARCHAR(20)     NOT NULL,   -- user / assistant
    content           TEXT            NOT NULL,
    created_at        TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

-- 消息按对话检索索引
CREATE INDEX IF NOT EXISTS messages_conversation_id_idx
    ON messages (conversation_id);

-- ============================================================
-- 9. 初始超级管理员账号（密码：Admin@123456）
-- 密码哈希由 bcrypt 生成，上线后请通过系统修改密码
-- ============================================================
INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified)
VALUES (
    'admin',
    'admin@neikongai.com',
    '$2b$12$CwVSgJ1Ppbk56VQgOBxFc.o2OZR59wu3L0jCgTI7MoYruHxbWl.Uq',  -- Admin@123456
    '超级管理员',
    'super_admin',
    TRUE,
    TRUE
)
ON CONFLICT (username) DO NOTHING;
