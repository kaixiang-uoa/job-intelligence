"""
基础适配器抽象类

提供可扩展的设计，方便未来添加新的求职平台（LinkedIn, Glassdoor 等）
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.job_posting_dto import JobPostingDTO, ScrapeRequest


class BaseJobAdapter(ABC):
    """
    求职平台适配器基类

    所有具体的平台适配器（Indeed, SEEK, LinkedIn 等）都应该继承此类
    并实现 scrape() 方法。

    设计原则：
    1. 统一接口：所有适配器返回相同的 JobPostingDTO 列表
    2. 可扩展性：新平台只需继承此类并实现 scrape()
    3. 配置隔离：每个适配器管理自己的平台特定配置
    """

    def __init__(self, config: Optional[dict] = None):
        """
        初始化适配器

        Args:
            config: 平台特定配置（可选）
        """
        self.config = config or {}
        self._setup()

    def _setup(self):
        """
        适配器初始化设置（子类可选实现）

        用于：
        - 设置请求头
        - 初始化 API 客户端
        - 加载配置
        """
        pass

    @abstractmethod
    def scrape(self, request: ScrapeRequest) -> List[JobPostingDTO]:
        """
        抓取职位数据（所有子类必须实现）

        Args:
            request: 爬取请求参数

        Returns:
            标准化的职位数据列表

        Raises:
            ScraperException: 爬取失败时抛出
        """
        pass

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """
        平台名称（所有子类必须实现）

        Returns:
            平台标识（如 "indeed", "seek", "linkedin"）
        """
        pass

    def validate_request(self, request: ScrapeRequest) -> bool:
        """
        验证请求参数（子类可选实现）

        Args:
            request: 爬取请求参数

        Returns:
            验证是否通过
        """
        # 基础验证：关键词不能为空
        if not request.keywords or not request.keywords.strip():
            raise ValueError("Keywords cannot be empty")

        return True

    def _generate_id(self, job_data: dict) -> str:
        """
        生成职位 ID（当平台不提供 ID 时）

        Args:
            job_data: 职位原始数据

        Returns:
            生成的唯一 ID
        """
        import hashlib

        # 使用标题 + 公司 + 平台生成哈希
        unique_str = f"{job_data.get('title', '')}_{job_data.get('company', '')}_{self.platform_name}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:16]


class ScraperException(Exception):
    """爬虫异常基类"""

    def __init__(self, message: str, platform: str, original_error: Optional[Exception] = None):
        self.message = message
        self.platform = platform
        self.original_error = original_error
        super().__init__(self.message)


class RateLimitException(ScraperException):
    """速率限制异常"""
    pass


class PlatformException(ScraperException):
    """平台错误异常（API 返回错误）"""
    pass
