"""
爬虫异常类定义

定义细粒度的异常类型，便于:
1. 精准的错误处理和日志记录
2. 更好的 API 错误响应
3. 调试和问题排查
"""

from typing import Optional


# ========================================
# 基础异常类
# ========================================

class ScraperException(Exception):
    """
    爬虫异常基类

    所有爬虫相关异常的父类
    """

    def __init__(
        self,
        message: str,
        platform: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Args:
            message: 错误描述
            platform: 平台名称（seek, indeed 等）
            original_error: 原始异常对象
        """
        self.message = message
        self.platform = platform
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self):
        if self.platform:
            return f"[{self.platform}] {self.message}"
        return self.message


# ========================================
# 网络相关异常
# ========================================

class ScraperNetworkError(ScraperException):
    """
    网络错误异常

    用于:
    - 网络超时
    - 连接失败
    - DNS 解析错误
    """
    pass


class ScraperTimeoutError(ScraperNetworkError):
    """
    超时异常

    用于:
    - API 请求超时
    - 响应超时
    """
    pass


class RateLimitException(ScraperNetworkError):
    """
    速率限制异常

    用于:
    - API 限流（429 Too Many Requests）
    - 请求频率过高
    """

    def __init__(
        self,
        message: str,
        platform: Optional[str] = None,
        retry_after: Optional[int] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Args:
            retry_after: 建议重试间隔（秒）
        """
        super().__init__(message, platform, original_error)
        self.retry_after = retry_after


# ========================================
# 数据相关异常
# ========================================

class ScraperDataError(ScraperException):
    """
    数据格式错误异常

    用于:
    - JSON 解析失败
    - 数据格式不符合预期
    - 缺少必需字段
    """
    pass


class ScraperValidationError(ScraperException):
    """
    数据验证异常

    用于:
    - 请求参数验证失败
    - 数据字段验证失败
    - 业务规则验证失败
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        platform: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Args:
            field: 验证失败的字段名
        """
        super().__init__(message, platform, original_error)
        self.field = field


class ScraperParsingError(ScraperDataError):
    """
    数据解析异常

    用于:
    - HTML 解析失败
    - 数据提取失败
    - 字段转换失败
    """
    pass


# ========================================
# API 相关异常
# ========================================

class PlatformException(ScraperException):
    """
    平台 API 错误异常

    用于:
    - API 返回错误状态码（4xx, 5xx）
    - API 返回错误消息
    """

    def __init__(
        self,
        message: str,
        platform: Optional[str] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Args:
            status_code: HTTP 状态码
            response_body: 响应体内容
        """
        super().__init__(message, platform, original_error)
        self.status_code = status_code
        self.response_body = response_body


class ScraperAuthenticationError(PlatformException):
    """
    认证错误异常

    用于:
    - API 密钥无效
    - 认证令牌过期
    - 权限不足
    """
    pass


class ScraperNotFoundError(PlatformException):
    """
    资源不存在异常

    用于:
    - API 端点不存在（404）
    - 职位已下架
    """
    pass


# ========================================
# 配置相关异常
# ========================================

class ScraperConfigurationError(ScraperException):
    """
    配置错误异常

    用于:
    - 缺少必需配置
    - 配置值无效
    - 环境变量未设置
    """
    pass


# ========================================
# 辅助函数
# ========================================

def classify_http_error(status_code: int, platform: str, message: str = None) -> PlatformException:
    """
    根据 HTTP 状态码分类异常

    Args:
        status_code: HTTP 状态码
        platform: 平台名称
        message: 自定义错误消息

    Returns:
        对应的异常对象

    Example:
        >>> try:
        ...     response.raise_for_status()
        ... except requests.HTTPError as e:
        ...     raise classify_http_error(response.status_code, "seek")
    """
    default_message = message or f"HTTP {status_code} error"

    if status_code == 401 or status_code == 403:
        return ScraperAuthenticationError(
            message=message or "Authentication failed",
            platform=platform,
            status_code=status_code
        )
    elif status_code == 404:
        return ScraperNotFoundError(
            message=message or "Resource not found",
            platform=platform,
            status_code=status_code
        )
    elif status_code == 429:
        return RateLimitException(
            message=message or "Rate limit exceeded",
            platform=platform
        )
    elif 400 <= status_code < 500:
        return PlatformException(
            message=message or f"Client error: {status_code}",
            platform=platform,
            status_code=status_code
        )
    elif 500 <= status_code < 600:
        return PlatformException(
            message=message or f"Server error: {status_code}",
            platform=platform,
            status_code=status_code
        )
    else:
        return PlatformException(
            message=default_message,
            platform=platform,
            status_code=status_code
        )
