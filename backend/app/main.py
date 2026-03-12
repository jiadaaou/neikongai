from app.routers import admin_standards
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# 导入路由
from app.routers import admin_laws
from app.routers import auth, chat, ai_test, files, users, ai_ask, query_understanding

# 加载环境变量
load_dotenv()

# 创建 FastAPI 应用
app = FastAPI(
    title="NeikongAI API",
    description="多租户法律知识库 + 企业内控系统 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 跨域配置
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由（所有路由统一在 router 文件里定义 prefix）
app.include_router(auth.router, tags=["认证"])
app.include_router(chat.router, tags=["对话"])
app.include_router(ai_test.router, tags=["AI Test"])
app.include_router(query_understanding.router, tags=["AI-Query-Understanding"])
app.include_router(files.router, tags=["文件"])
app.include_router(users.router, tags=["用户"])
app.include_router(ai_ask.router, tags=["AI-Answer"])
app.include_router(admin_laws.router, tags=["Admin-Laws"])
app.include_router(admin_standards.router, tags=["Admin-Standards"])

# 根路由
@app.get("/")
async def root():
    return {
        "message": "欢迎使用 NeikongAI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "description": "多租户法律知识库 + 企业内控系统",
        "mode": "开发模式 - 已禁用认证"
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "neikongai-api"
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    print("🚀 NeikongAI API 启动成功！")
    print(f"📖 API 文档地址: http://localhost:8000/docs")
    print("⚠️  开发模式：已禁用认证")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    print("👋 NeikongAI API 已关闭")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
