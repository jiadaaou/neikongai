from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

# 枚举类型定义
class UserRole(str, enum.Enum):
    """用户角色"""
    SUPER_ADMIN = "super_admin"      # 平台超级管理员
    COMPANY_ADMIN = "company_admin"  # 企业管理员
    COMPANY_USER = "company_user"    # 企业普通用户

class KnowledgeBaseType(str, enum.Enum):
    """知识库类型"""
    PLATFORM = "platform"  # 平台法律知识库（所有企业共享）
    COMPANY = "company"    # 企业私有知识库

class DocumentStatus(str, enum.Enum):
    """文档状态"""
    PENDING = "pending"      # 待处理
    PROCESSING = "processing"  # 处理中（向量化中）
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败


# 企业表
class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, comment="企业名称")
    code = Column(String(50), unique=True, nullable=False, comment="企业代码/统一社会信用代码")
    contact_name = Column(String(100), comment="联系人姓名")
    contact_email = Column(String(100), comment="联系人邮箱")
    contact_phone = Column(String(20), comment="联系人电话")
    
    # MinIO 配置
    minio_bucket_docs = Column(String(100), comment="文档存储桶名称")
    minio_bucket_avatars = Column(String(100), comment="头像储存桶名称")
    minio_bucket_exports = Column(String(100), comment="导出文件存储桶名称")
    
    # ChromaDB 配置
    chroma_collection_name = Column(String(100), comment="ChromaDB 集合名称")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    storage_quota = Column(Integer, default=10737418240, comment="存储配额(字节)，默认10GB")
    storage_used = Column(Integer, default=0, comment="已使用存储(字节)")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    users = relationship("User", back_populates="company")
    documents = relationship("Document", back_populates="company")


# 用户表
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    hashed_password = Column(String(200), nullable=False, comment="加密后的密码")
    full_name = Column(String(100), comment="真实姓名")
    phone = Column(String(20), comment="手机号")
    avatar_url = Column(String(500), comment="头像URL")
    
    # 角色和权限
    role = Column(SQLEnum(UserRole), default=UserRole.COMPANY_USER, comment="用户角色")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, comment="所属企业ID，NULL表示平台管理员")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_verified = Column(Boolean, default=False, comment="是否已验证邮箱")
    last_login = Column(DateTime(timezone=True), comment="最后登录时间")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    company = relationship("Company", back_populates="users")


# 文档表
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, comment="文档标题")
    filename = Column(String(500), nullable=False, comment="文件名")
    file_size = Column(Integer, comment="文件大小(字节)")
    file_type = Column(String(50), comment="文件类型(pdf/docx等)")
    
    # 存储信息
    file_url = Column(String(1000), nullable=False, comment="MinIO 文件URL")
    minio_bucket = Column(String(100), comment="MinIO 存储桶名称")
    minio_object_name = Column(String(500), comment="MinIO 对象名称")
    
    # 内容
    content = Column(Text, comment="提取的文本内容")
    content_summary = Column(Text, comment="内容摘要")
    
    # 知识库分类
    knowledge_base_type = Column(
        SQLEnum(KnowledgeBaseType),
        nullable=False,
        comment="知识库类型：platform=平台共享，company=企业私有"
    )
    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=True,
        comment="所属企业ID，NULL表示平台知识库"
    )
    
    # 向量化信息
    vector_id = Column(String(100), comment="ChromaDB 向量ID")
    chroma_collection = Column(String(100), comment="ChromaDB 集合名称")
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, comment="处理状态")
    
    # 元数据（改名避免冲突）
    meta_data = Column(JSON, comment="额外元数据（标签、分类等）")
    tags = Column(JSON, comment="标签数组")
    
    # 上传信息
    uploaded_by = Column(Integer, ForeignKey("users.id"), comment="上传者ID")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    company = relationship("Company", back_populates="documents")
