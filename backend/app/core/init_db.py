from app.core.database import engine, Base
from app.models.models import Company, User, Document

def init_db():
    """
    初始化数据库
    创建所有表结构
    """
    print("🔧 开始创建数据库表...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    print("✅ 数据库表创建成功！")
    print("📋 已创建的表：")
    print("  - companies (企业表)")
    print("  - users (用户表)")
    print("  - documents (文档表)")

if __name__ == "__main__":
    init_db()
