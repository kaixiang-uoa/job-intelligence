"""
SEEK 职位数据适配器

使用 SEEK 内部 GraphQL API 获取职位数据
"""

import logging
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.job_posting_dto import JobPostingDTO, ScrapeRequest, PlatformEnum
from app.adapters.base_adapter import BaseJobAdapter
from app.utils.location_parser import parse_location
from app.utils.trade_extractor import extract_trade
from app.utils.employment_type import normalize_employment_type
from app.utils.salary_parser import parse_salary_range
from app.utils.html_cleaner import clean_html
from app.exceptions import (
    ScraperNetworkError,
    ScraperTimeoutError,
    ScraperDataError,
    ScraperValidationError,
    ScraperParsingError,
    PlatformException,
    classify_http_error
)

logger = logging.getLogger(__name__)


class SeekAdapter(BaseJobAdapter):
    """
    SEEK 职位数据适配器

    继承自 BaseJobAdapter，实现 scrape() 方法
    使用 SEEK 内部 GraphQL API 获取职位数据
    """

    def __init__(self):
        """
        初始化 SEEK 适配器

        配置:
            - API 端点: SEEK GraphQL API
            - Headers: 必需的请求头（User-Agent, seek-request-brand 等）
            - GraphQL Query: 职位搜索查询模板
        """
        super().__init__()

        # SEEK REST API 端点（内部 API）
        self.api_url = "https://www.seek.com.au/api/jobsearch/v5/search"

        # 必需的请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }

        logger.info("SeekAdapter initialized")

    @property
    def platform_name(self) -> str:
        """平台名称"""
        return "seek"

    def scrape(self, request: ScrapeRequest) -> List[JobPostingDTO]:
        """
        抓取 SEEK 职位数据

        Args:
            request: 爬取请求参数（包含 keywords, location, max_results）

        Returns:
            List[JobPostingDTO]: 标准化的职位列表

        Raises:
            ValueError: 参数无效
            requests.RequestException: API 调用失败
        """
        # 验证请求
        self.validate_request(request)

        # 提取参数
        keywords = request.keywords
        location = request.location
        results_wanted = request.max_results if request.max_results else 50

        if results_wanted < 1 or results_wanted > 50:
            logger.warning(f"results_wanted={results_wanted} 超出范围，调整为 50")
            results_wanted = 50

        logger.info(f"开始抓取 SEEK 职位: keywords={keywords}, location={location}, results_wanted={results_wanted}")

        try:
            # 1. 构建 URL 参数
            params = self._build_params(keywords, location, results_wanted)

            # 2. 调用 SEEK API
            data = self._call_seek_api(params)

            # 3. 提取职位列表
            jobs_data = data.get("data", [])
            total_count = data.get("totalCount", len(jobs_data))

            logger.info(f"SEEK API 返回 {len(jobs_data)} 个职位（总计 {total_count}）")

            # 4. 转换每个职位
            jobs = []
            failed_count = 0
            validation_errors = 0
            parsing_errors = 0

            for job_data in jobs_data:
                try:
                    job_dto = self._transform_job(job_data)
                    if job_dto:
                        jobs.append(job_dto)
                except ScraperValidationError as e:
                    # 验证错误（缺少必需字段）- 跳过该职位
                    validation_errors += 1
                    failed_count += 1
                    job_id = job_data.get("id", "unknown")
                    logger.warning(f"职位 {job_id} 验证失败: {e.message}")
                except ScraperParsingError as e:
                    # 解析错误（数据转换失败）- 跳过该职位
                    parsing_errors += 1
                    failed_count += 1
                    job_id = job_data.get("id", "unknown")
                    logger.warning(f"职位 {job_id} 解析失败: {e.message}")
                except Exception as e:
                    # 未知错误 - 跳过该职位
                    failed_count += 1
                    job_id = job_data.get("id", "unknown")
                    logger.warning(f"职位 {job_id} 转换失败（未知错误）: {e}")

            if failed_count > 0:
                logger.warning(
                    f"{failed_count} 个职位转换失败 "
                    f"(验证错误: {validation_errors}, 解析错误: {parsing_errors}, "
                    f"其他: {failed_count - validation_errors - parsing_errors})"
                )

            # 🔧 FIX: 去重 - 基于 source_id
            original_count = len(jobs)
            jobs = self._deduplicate_by_source_id(jobs)
            duplicates_removed = original_count - len(jobs)

            if duplicates_removed > 0:
                logger.warning(f"移除了 {duplicates_removed} 个重复职位（基于 source_id）")

            logger.info(f"成功转换 {len(jobs)} 个职位（去重后）")
            return jobs

        except (ScraperNetworkError, ScraperTimeoutError, ScraperDataError, PlatformException):
            # 这些是致命错误，直接向上传递
            raise
        except Exception as e:
            logger.error(f"SEEK 抓取失败（未知错误）: {e}")
            raise ScraperException(
                message=f"SEEK 抓取失败: {str(e)}",
                platform=self.platform_name,
                original_error=e
            )

    def _build_params(self, keywords: str, location: str, results_wanted: int) -> dict:
        """
        构建 SEEK REST API URL 参数

        Args:
            keywords: 搜索关键词
            location: 地点（如 Sydney, Melbourne）
            results_wanted: 期望结果数量

        Returns:
            dict: URL 查询参数
        """
        # 🔧 FIX (2025-12-26): 地点过滤修复
        # 之前硬编码 "where": "All Australia"，导致地点过滤失效
        # 现在使用用户指定的 location 参数
        # 测试结果：Sydney 搜索 100% 返回 NSW 职位
        params = {
            "siteKey": "AU-Main",
            "where": location,  # 使用用户指定的地点（修复后）
            "keywords": keywords,
            "page": 1,
            "pageSize": results_wanted,
            "locale": "en-AU"
        }

        return params

    def _call_seek_api(self, params: dict) -> dict:
        """
        调用 SEEK REST API

        Args:
            params: URL 查询参数

        Returns:
            dict: API 响应数据

        Raises:
            ScraperTimeoutError: 请求超时
            ScraperNetworkError: 网络错误
            PlatformException: API 返回错误状态码
            ScraperDataError: 响应格式错误
        """
        try:
            response = requests.get(
                url=self.api_url,
                params=params,
                headers=self.headers,
                timeout=30  # 30 秒超时
            )

            # 检查 HTTP 状态码
            response.raise_for_status()

            # 解析 JSON
            try:
                response_data = response.json()
            except ValueError as e:
                logger.error(f"SEEK API 响应不是有效的 JSON: {e}")
                raise ScraperDataError(
                    message="API 响应不是有效的 JSON",
                    platform=self.platform_name,
                    original_error=e
                )

            # 验证响应格式
            if "data" not in response_data:
                logger.error("SEEK API 响应缺少 'data' 字段")
                raise ScraperDataError(
                    message="API 响应缺少 'data' 字段",
                    platform=self.platform_name
                )

            return response_data

        except requests.Timeout as e:
            logger.error(f"SEEK API 超时: {e}")
            raise ScraperTimeoutError(
                message="SEEK API 请求超时（30秒）",
                platform=self.platform_name,
                original_error=e
            )
        except requests.HTTPError as e:
            logger.error(f"SEEK API HTTP 错误: {e}")
            raise classify_http_error(
                status_code=response.status_code,
                platform=self.platform_name,
                message=f"SEEK API 返回错误: {response.status_code}"
            )
        except requests.ConnectionError as e:
            logger.error(f"SEEK API 连接错误: {e}")
            raise ScraperNetworkError(
                message="无法连接到 SEEK API",
                platform=self.platform_name,
                original_error=e
            )
        except requests.RequestException as e:
            logger.error(f"SEEK API 请求失败: {e}")
            raise ScraperNetworkError(
                message=f"SEEK API 请求失败: {str(e)}",
                platform=self.platform_name,
                original_error=e
            )

    def _deduplicate_by_source_id(self, jobs: List[JobPostingDTO]) -> List[JobPostingDTO]:
        """
        基于 source_id 去重

        🔧 FIX (2025-12-26): Python 适配器层去重
        解决 SEEK API 可能返回重复职位的问题（同一 source_id 出现多次）

        这是第一层去重（Python 层），数据库层还有第二层去重（fingerprint + content_hash）
        双层去重确保数据质量：
        - Python 层：防止单次抓取中的重复（性能优化）
        - 数据库层：防止多次抓取间的重复（数据完整性）

        Args:
            jobs: 职位列表

        Returns:
            List[JobPostingDTO]: 去重后的职位列表
        """
        seen_ids = set()
        unique_jobs = []

        for job in jobs:
            if job.source_id not in seen_ids:
                seen_ids.add(job.source_id)
                unique_jobs.append(job)
            else:
                logger.debug(f"发现重复职位: {job.source_id} - {job.title}")

        return unique_jobs

    def _extract_description(self, job_data: dict) -> Optional[str]:
        """
        从 SEEK API 数据中提取职位描述

        优先级:
            1. job_data.get("teaser")         # HTML 片段
            2. job_data.get("bulletPoints")   # 要点列表
            3. None

        Args:
            job_data: SEEK API 返回的职位对象

        Returns:
            str or None: 清理后的描述文本（限制 500 字符）
        """
        # 尝试提取 teaser
        teaser = job_data.get("teaser")
        if teaser:
            description = clean_html(teaser)
            if description and len(description) > 500:
                description = description[:500] + "..."
            return description

        # 尝试提取 bulletPoints
        bullet_points = job_data.get("bulletPoints", [])
        if bullet_points:
            description = " • ".join(bullet_points)
            if len(description) > 500:
                description = description[:500] + "..."
            return description

        return None

    def _transform_job(self, job_data: dict) -> Optional[JobPostingDTO]:
        """
        将 SEEK API 返回的单个职位转换为 JobPostingDTO

        Args:
            job_data: SEEK API 返回的职位对象

        Returns:
            JobPostingDTO or None（转换失败时返回 None）

        Raises:
            ScraperValidationError: 缺少必需字段
            ScraperParsingError: 数据解析失败
        """
        try:
            # 提取基本字段（SEEK REST API 格式）
            job_id = job_data.get("id")
            title = job_data.get("title")

            # 验证必需字段
            if not job_id:
                logger.warning("职位缺少必需字段: id")
                raise ScraperValidationError(
                    message="职位缺少必需字段: id",
                    field="id",
                    platform=self.platform_name
                )

            if not title:
                logger.warning(f"职位 {job_id} 缺少必需字段: title")
                raise ScraperValidationError(
                    message=f"职位 {job_id} 缺少必需字段: title",
                    field="title",
                    platform=self.platform_name
                )

            # 提取公司名称（advertiser.description）
            advertiser = job_data.get("advertiser", {})
            company = advertiser.get("description") or job_data.get("companyName") or job_data.get("employer", {}).get("name")

            # 提取地点（locations 数组的第一个元素）
            locations = job_data.get("locations", [])
            location_label = ""
            if locations and len(locations) > 0:
                location_label = locations[0].get("label", "")
            state, suburb = parse_location(location_label)  # parse_location 返回 (state, suburb)

            # 提取描述
            description = self._extract_description(job_data)

            # 解析薪资范围（salaryLabel 字符串）
            salary_str = job_data.get("salaryLabel")
            min_amount, max_amount = parse_salary_range(salary_str)

            # 提取工作类型（workTypes 数组的第一个元素）
            work_types = job_data.get("workTypes", [])
            work_type = work_types[0] if work_types else None
            job_type = normalize_employment_type(work_type)

            # 提取 trade
            trade = extract_trade(title)

            # 提取发布时间（listingDate）
            created_at = job_data.get("listingDate")

            # 构建职位 URL
            job_url = f"https://www.seek.com.au/job/{job_id}"

            # 解析发布时间（如果是字符串，转换为 datetime）
            posted_at = None
            if created_at:
                if isinstance(created_at, str):
                    try:
                        posted_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except ValueError as e:
                        logger.warning(f"职位 {job_id} 日期解析失败: {created_at}, 错误: {e}")
                        # 日期解析失败不影响其他数据，继续处理
                        posted_at = None
                elif isinstance(created_at, datetime):
                    posted_at = created_at

            # 创建 DTO（使用正确的字段名）
            try:
                return JobPostingDTO(
                    source=PlatformEnum.SEEK,
                    source_id=str(job_id),
                    title=title,
                    company=company or "Unknown",  # company 是必需字段
                    location_suburb=suburb,
                    location_state=state,
                    trade=trade,
                    employment_type=job_type,
                    pay_range_min=min_amount,
                    pay_range_max=max_amount,
                    description=description,
                    posted_at=posted_at,
                    job_url=job_url
                )
            except Exception as e:
                logger.error(f"职位 {job_id} DTO 创建失败: {e}")
                raise ScraperParsingError(
                    message=f"职位 {job_id} DTO 创建失败",
                    platform=self.platform_name,
                    original_error=e
                )

        except ScraperValidationError:
            # 验证错误直接向上传递
            raise
        except ScraperParsingError:
            # 解析错误直接向上传递
            raise
        except Exception as e:
            logger.error(f"职位转换失败（未知错误）: {e}")
            return None
