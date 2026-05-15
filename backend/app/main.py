from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.rate_limit import limiter
from app.routers import auth, tags, problems, knowledge
from app.routers.submission import router as submission_router

app = FastAPI(
    title="AI_code_assisstant API",
    description="AI 编程学习平台后端 API",
    version="0.1.0"
)

# 注册速率限制异常处理
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1")
app.include_router(tags.router, prefix="/api/v1")
app.include_router(problems.router, prefix="/api/v1")
app.include_router(submission_router)
app.include_router(knowledge.router)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Welcome to AI_code_assisstant API", "version": "0.1.0"}