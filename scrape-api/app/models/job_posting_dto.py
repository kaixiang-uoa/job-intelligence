"""
统一的职位数据模型

此模型对应 .NET 后端的 JobPosting 实体，确保数据格式一致
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class PlatformEnum(str, Enum):
    """支持的求职平台枚举（可扩展）"""
    INDEED = "indeed"
    SEEK = "seek"
    # 🔖 未来可扩展的平台
    # LINKEDIN = "linkedin"
    # GLASSDOOR = "glassdoor"
    # GOOGLE_JOBS = "google_jobs"


class JobPostingDTO(BaseModel):
    """
    标准化的职位数据传输对象

    映射到 .NET JobPosting 实体的所有字段
    """

    # 必需字段
    source: PlatformEnum = Field(..., description="数据源平台")
    source_id: str = Field(..., description="平台的职位 ID")
    title: str = Field(..., description="职位标题")
    company: str = Field(..., description="公司名称")

    # 地点信息
    location_state: Optional[str] = Field(None, description="州/省（如 SA, NSW）")
    location_suburb: Optional[str] = Field(None, description="城市/郊区（如 Adelaide）")

    # 职位属性
    trade: Optional[str] = Field(None, description="行业/工种（如 tiler, plumber）")
    employment_type: Optional[str] = Field(None, description="雇佣类型（Full Time, Part Time）")

    # 薪资信息
    pay_range_min: Optional[float] = Field(None, description="最低薪资")
    pay_range_max: Optional[float] = Field(None, description="最高薪资")

    # 详细信息
    description: Optional[str] = Field(None, description="职位描述（纯文本或 Markdown）")
    requirements: Optional[str] = Field(None, description="职位要求")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")

    # 时间戳
    posted_at: Optional[datetime] = Field(None, description="发布时间")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, description="爬取时间")

    # 扩展字段（可选，未来可用）
    job_url: Optional[str] = Field(None, description="职位链接")
    is_remote: Optional[bool] = Field(None, description="是否远程")
    company_url: Optional[str] = Field(None, description="公司网站")

    class Config:
        """Pydantic 配置"""
        use_enum_values = True  # 自动转换 Enum 为字符串
        json_schema_extra = {
            "example": {
                "source": "indeed",
                "source_id": "abc123def456",
                "title": "Experienced Tiler - Adelaide",
                "company": "Premier Tiling Services",
                "location_state": "SA",
                "location_suburb": "Adelaide",
                "trade": "tiler",
                "employment_type": "Full Time",
                "pay_range_min": 70000.0,
                "pay_range_max": 85000.0,
                "description": "We are seeking an experienced tiler...",
                "requirements": "- 5+ years experience\n- White Card",
                "tags": ["trades", "construction", "full-time"],
                "posted_at": "2025-12-15T08:00:00Z",
                "job_url": "https://au.indeed.com/viewjob?jk=abc123",
                "is_remote": False
            }
        }

    @field_validator('title', 'company')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """验证必需字符串字段不为空"""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()

    @field_validator('tags', mode='before')
    @classmethod
    def ensure_list(cls, v):
        """确保 tags 是列表"""
        if v is None:
            return []
        if isinstance(v, str):
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v


class ScrapeRequest(BaseModel):
    """
    爬取请求参数

    用于 API 端点接收用户请求
    """

    keywords: str = Field(..., description="搜索关键词", min_length=1)
    location: str = Field(..., description="地点（如 Adelaide, Sydney）")
    max_results: int = Field(default=50, description="最大结果数", ge=1, le=200)

    # 可选的平台特定参数
    classification: Optional[str] = Field(None, description="职位分类 ID（SEEK 特有）")
    job_type: Optional[str] = Field(None, description="工作类型过滤")

    class Config:
        json_schema_extra = {
            "example": {
                "keywords": "tiler",
                "location": "Adelaide",
                "max_results": 50,
                "classification": "1225"  # SEEK Trades & Services
            }
        }


class ScrapeResponse(BaseModel):
    """
    爬取响应

    用于 API 端点返回结果
    """

    platform: PlatformEnum = Field(..., description="数据源平台")
    jobs: List[JobPostingDTO] = Field(..., description="职位列表")
    count: int = Field(..., description="职位数量")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, description="爬取时间")

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "indeed",
                "jobs": [
                    {
                        "source": "indeed",
                        "source_id": "abc123",
                        "title": "Tiler",
                        "company": "ABC Company",
                        "location_state": "SA",
                        "location_suburb": "Adelaide"
                    }
                ],
                "count": 1,
                "scraped_at": "2025-12-18T12:00:00Z"
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应"""

    status: str = Field(default="ok", description="服务状态")
    version: str = Field(..., description="API 版本")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="当前时间")
    platforms: List[str] = Field(..., description="支持的平台列表")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "version": "1.0.0",
                "timestamp": "2025-12-18T12:00:00Z",
                "platforms": ["indeed", "seek"]
            }
        }
