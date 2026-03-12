from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neikongai_user:password@localhost:5432/neikongai"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 自动检测断开的连接
    pool_size=20,        # 连接池大小
    max_overflow=10,     # 超出连接池大小时最多创建的连接数
    echo=False           # 不打印 SQL 语句（生产环境）
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建基类
Base = declarative_base()

# 依赖注入：获取数据库会话
def get_db():
    """
    数据库会话依赖
    使用 yield 确保请求结束后关闭连接
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 原始 psycopg2 连接（用于不使用 ORM 的场景）
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """
    获取原始 psycopg2 数据库连接
    用于需要直接执行 SQL 的场景
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "neikongai"),
        user=os.getenv("DB_USER", "neikongai_user"),
        password=os.getenv("DB_PASSWORD", "password")
    )
