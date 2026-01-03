"""
FastAPI 应用入口

提供爬虫 API 服务
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.config.settings import settings
from app.models.job_posting_dto import (
    HealthResponse,
    ScrapeRequest,
    ScrapeResponse,
    PlatformEnum
)

# 配置日志
logger.remove()  # 移除默认处理器
logger.add(
    sys.stdout,
    format=settings.log_format,
    level=settings.log_level,
    colorize=True
)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Job Intelligence 爬虫 API - 支持 Indeed 和 SEEK 平台",
    docs_url="/docs" if settings.debug else None,  # 生产环境禁用文档
    redoc_url="/redoc" if settings.debug else None,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# 健康检查端点
# ============================================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="健康检查",
    description="检查 API 服务状态"
)
async def health_check():
    """
    健康检查端点

    返回：
    - 服务状态
    - API 版本
    - 当前时间
    - 支持的平台列表
    """
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        platforms=settings.supported_platforms
    )


@app.get(
    "/",
    tags=["System"],
    summary="API 根路径",
    description="返回 API 基本信息"
)
async def root():
    """根路径"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Disabled in production",
        "health": "/health"
    }


# ============================================================================
# Indeed 爬虫端点
# ============================================================================

@app.post(
    "/scrape/indeed",
    response_model=ScrapeResponse,
    tags=["Scraper"],
    summary="抓取 Indeed 职位",
    description="使用 JobSpy 库抓取 Indeed 平台的职位数据"
)
async def scrape_indeed(request: ScrapeRequest):
    """
    抓取 Indeed 职位

    参数：
    - keywords: 搜索关键词（必需）
    - location: 地点（必需）
    - max_results: 最大结果数（默认 50）

    返回：
    - 标准化的职位数据列表
    """
    try:
        from app.adapters.indeed_adapter import IndeedAdapter
        from datetime import datetime

        logger.info(f"Scraping Indeed: keywords={request.keywords}, location={request.location}")

        # 使用 Indeed 适配器
        adapter = IndeedAdapter()
        jobs = adapter.scrape(request)

        logger.info(f"Successfully scraped {len(jobs)} jobs from Indeed")

        return ScrapeResponse(
            platform=PlatformEnum.INDEED,
            jobs=jobs,
            count=len(jobs),
            scraped_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"Indeed scraping failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {str(e)}"
        )


# ============================================================================
# SEEK 爬虫端点
# ============================================================================

@app.post(
    "/scrape/seek",
    response_model=ScrapeResponse,
    tags=["Scraper"],
    summary="抓取 SEEK 职位",
    description="使用 SEEK 内部 API 抓取职位数据"
)
async def scrape_seek(request: ScrapeRequest):
    """
    抓取 SEEK 职位

    参数：
    - keywords: 搜索关键词（必需）
    - location: 地点（可选）
    - max_results: 最大结果数（默认 50）

    返回：
    - 标准化的职位数据列表
    """
    try:
        from app.adapters.seek_adapter import SeekAdapter
        from datetime import datetime

        logger.info(f"Scraping SEEK: keywords={request.keywords}, location={request.location}")

        # 使用 SEEK 适配器
        adapter = SeekAdapter()
        jobs = adapter.scrape(request)

        logger.info(f"Successfully scraped {len(jobs)} jobs from SEEK")

        return ScrapeResponse(
            platform=PlatformEnum.SEEK,
            jobs=jobs,
            count=len(jobs),
            scraped_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"SEEK scraping failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scraping failed: {str(e)}"
        )


# ============================================================================
# 全局异常处理
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An error occurred"
        }
    )


# ============================================================================
# 应用生命周期事件
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Supported platforms: {', '.join(settings.supported_platforms)}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info(f"Shutting down {settings.app_name}")


# ============================================================================
# 运行说明
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
