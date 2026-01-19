"""
Indeed 平台适配器

使用 JobSpy 库抓取 Indeed 职位数据并转换为统一的 JobPostingDTO 格式
"""

from typing import List
from datetime import datetime, timezone
from loguru import logger

try:
    from jobspy import scrape_jobs
except ImportError:
    logger.warning("JobSpy library not installed. Indeed scraping will not work.")
    scrape_jobs = None

from app.adapters.base_adapter import BaseJobAdapter, ScraperException
from app.models.job_posting_dto import JobPostingDTO, ScrapeRequest, PlatformEnum
from app.utils.location_parser import parse_location
from app.utils.trade_extractor import extract_trade
from app.utils.employment_type import normalize_employment_type
from app.config.settings import settings


class IndeedAdapter(BaseJobAdapter):
    """
    Indeed 平台适配器

    使用 JobSpy 库抓取 Indeed 职位数据
    """

    @property
    def platform_name(self) -> str:
        """平台名称"""
        return "indeed"

    def _deduplicate_by_source_id(self, jobs: List[JobPostingDTO]) -> List[JobPostingDTO]:
        """
        基于 source_id 去重

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

    def scrape(self, request: ScrapeRequest) -> List[JobPostingDTO]:
        """
        抓取 Indeed 职位数据

        Args:
            request: 抓取请求参数

        Returns:
            List[JobPostingDTO]: 职位数据列表

        Raises:
            ScraperException: 抓取失败时抛出
        """
        # 验证请求参数
        self.validate_request(request)

        # 检查 JobSpy 是否可用
        if scrape_jobs is None:
            raise ScraperException("JobSpy library is not installed. Please run: pip install python-jobspy")

        logger.info(f"Starting Indeed scrape: keywords='{request.keywords}', location='{request.location}', max_results={request.max_results}")

        try:
            # 调用 JobSpy 抓取数据
            df = scrape_jobs(
                site_name=['indeed'],
                search_term=request.keywords,
                location=request.location,
                results_wanted=request.max_results,
                country_indeed=settings.indeed_country,
                hours_old=None,  # 不限制发布时间
            )

            logger.info(f"JobSpy returned {len(df)} results")

            # 转换数据
            jobs = []
            for idx, row in df.iterrows():
                try:
                    job = self._transform_job(row)
                    jobs.append(job)
                except Exception as e:
                    logger.warning(f"Failed to transform job at index {idx}: {e}")
                    continue

            # 🔧 FIX: 去重 - 基于 source_id
            original_count = len(jobs)
            jobs = self._deduplicate_by_source_id(jobs)
            duplicates_removed = original_count - len(jobs)

            if duplicates_removed > 0:
                logger.warning(f"移除了 {duplicates_removed} 个重复职位（基于 source_id）")

            # 📝 NOTE: Indeed API 搜索质量问题
            # Indeed 的搜索算法可能返回语义相关但非目标 trade 的职位
            # 例如：搜索 "carpenter" 可能返回 "Property Valuer"（房产估价师）
            # 这些职位的 trade 字段会是 None
            #
            # V1 MVP: 保持现状，用户可以通过 trade IS NOT NULL 过滤
            # V1.5 优化选项：
            #   1. 在此处添加后处理过滤，丢弃 trade=None 的职位
            #   2. 使用更精确的 Indeed API 参数（如果支持）
            #   3. 添加基于职位描述的二次验证
            #
            # 相关代码位置：
            #   - Trade 提取逻辑: app/utils/trade_extractor.py
            #   - 前端过滤: (待实现) WHERE trade IS NOT NULL

            logger.info(f"Successfully transformed {len(jobs)} jobs (after deduplication)")
            return jobs

        except Exception as e:
            logger.error(f"Indeed scraping failed: {e}")
            raise ScraperException(f"Failed to scrape Indeed: {str(e)}")

    def _transform_job(self, row) -> JobPostingDTO:
        """
        将 JobSpy 返回的 DataFrame 行转换为 JobPostingDTO

        Args:
            row: DataFrame 的一行数据

        Returns:
            JobPostingDTO: 标准化的职位数据
        """
        # 解析地点
        location_str = row.get('location', '')
        state, suburb = parse_location(location_str) if location_str else (None, None)

        # 提取 trade
        title = row.get('title', '')
        trade = extract_trade(title) if title else None

        # 标准化工作类型
        job_type = row.get('job_type')
        employment_type = normalize_employment_type(job_type) if job_type else None

        # 提取薪资范围
        min_amount = row.get('min_amount')
        max_amount = row.get('max_amount')

        # 确保薪资为 float 或 None
        pay_range_min = float(min_amount) if min_amount is not None and str(min_amount).replace('.', '').isdigit() else None
        pay_range_max = float(max_amount) if max_amount is not None and str(max_amount).replace('.', '').isdigit() else None

        # 处理发布时间
        # 🔧 FIX: 确保返回 UTC timezone-aware datetime，避免 PostgreSQL "Kind=Unspecified" 错误
        date_posted = row.get('date_posted')
        posted_at = None
        if date_posted is not None:
            try:
                if isinstance(date_posted, str):
                    # 解析 ISO 格式时间字符串并转换为 UTC
                    dt = datetime.fromisoformat(date_posted.replace('Z', '+00:00'))
                    # 确保是 timezone-aware 且为 UTC
                    if dt.tzinfo is None:
                        posted_at = dt.replace(tzinfo=timezone.utc)
                    else:
                        posted_at = dt.astimezone(timezone.utc)
                else:
                    # 确保已有的 datetime 也是 timezone-aware UTC
                    if date_posted.tzinfo is None:
                        posted_at = date_posted.replace(tzinfo=timezone.utc)
                    else:
                        posted_at = date_posted.astimezone(timezone.utc)
            except Exception as e:
                logger.debug(f"Failed to parse date_posted: {e}")

        # 生成 source_id
        job_id = row.get('id')
        if not job_id:
            job_id = self._generate_id({
                'title': title,
                'company': row.get('company', ''),
                'location': location_str
            })

        # 构建 JobPostingDTO
        job = JobPostingDTO(
            source=PlatformEnum.INDEED,
            source_id=str(job_id),
            title=title or 'Unknown',
            company=row.get('company', 'Unknown'),
            location_state=state,
            location_suburb=suburb,
            trade=trade,
            employment_type=employment_type,
            pay_range_min=pay_range_min,
            pay_range_max=pay_range_max,
            description=row.get('description'),
            requirements=None,  # Indeed 不单独提供 requirements
            tags=[],  # Indeed 不提供 tags
            posted_at=posted_at,
            scraped_at=datetime.utcnow(),
            job_url=row.get('job_url'),
            is_remote=row.get('is_remote'),
            company_url=row.get('company_url')
        )

        return job
