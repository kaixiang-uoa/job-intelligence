"""
应用配置管理

使用 pydantic-settings 从环境变量加载配置
支持 .env 文件
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """应用配置"""

    # FastAPI 配置
    app_name: str = "Job Intelligence Scraper API"
    app_version: str = "1.0.0"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # .NET Backend API 配置
    dotnet_api_url: str = "http://localhost:5000"

    # Indeed 配置
    indeed_country: str = "Australia"
    indeed_max_results: int = 50
    indeed_request_delay: int = 2  # 秒

    # SEEK 配置
    seek_base_url: str = "https://www.seek.com.au/api/jobsearch/v5/search"
    seek_site_key: str = "AU-Main"
    seek_locale: str = "en-AU"
    seek_request_delay: int = 2  # 秒
    seek_max_pages: int = 10

    # User-Agent 配置
    user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.4.1 Safari/605.1.15"
    )

    # 日志配置
    log_level: str = "INFO"
    log_format: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
        "<level>{message}</level>"
    )

    # Pydantic 配置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # 忽略额外的环境变量
    )

    @property
    def supported_platforms(self) -> List[str]:
        """返回支持的平台列表"""
        return ["indeed", "seek"]

    @property
    def cors_origins(self) -> List[str]:
        """CORS 允许的源（开发环境）"""
        if self.debug:
            return ["*"]  # 开发环境允许所有源
        return [
            "http://localhost:3000",  # 未来前端
            "http://localhost:5000",  # .NET Backend
        ]


# 全局配置实例
settings = Settings()
