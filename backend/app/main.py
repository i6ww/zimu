"""
自动打轴工具 - FastAPI 后端
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import upload, asr, export
from app.core.config import settings

# 创建 FastAPI 应用
app = FastAPI(
    title="自动打轴工具 API",
    description="基于阿里云百练 funASR 的字幕自动对齐服务",
    version="1.0.0"
)

# 配置 CORS（允许跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    error_msg = str(exc)
    if "payload too large" in error_msg.lower() or "max upload" in error_msg.lower():
        return JSONResponse(
            status_code=413,
            content={"detail": "文件过大，最大支持 500MB"}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": error_msg}
    )

# 注册路由
app.include_router(upload.router)
app.include_router(asr.router)
app.include_router(export.router)


@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "自动打轴工具 API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "storage_base_url": settings.storage_base_url
    }


# 运行入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
