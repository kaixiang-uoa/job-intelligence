"""
手动测试 Indeed 适配器

运行此脚本验证 Indeed 抓取功能是否正常工作
"""

import sys
from loguru import logger

# 配置日志
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}", level="INFO")


def test_indeed_adapter():
    """测试 Indeed 适配器"""
    from app.adapters.indeed_adapter import IndeedAdapter
    from app.models.job_posting_dto import ScrapeRequest

    logger.info("=" * 60)
    logger.info("Testing Indeed Adapter")
    logger.info("=" * 60)

    # 创建测试请求
    request = ScrapeRequest(
        keywords="tiler",
        location="Adelaide, SA",
        max_results=5  # 只抓取 5 个结果进行测试
    )

    logger.info(f"Request: keywords='{request.keywords}', location='{request.location}', max_results={request.max_results}")

    try:
        # 创建适配器
        adapter = IndeedAdapter()
        logger.info(f"Adapter platform: {adapter.platform_name}")

        # 执行抓取
        logger.info("Starting scrape...")
        jobs = adapter.scrape(request)

        # 输出结果
        logger.success(f"✅ Successfully scraped {len(jobs)} jobs")

        if jobs:
            logger.info("\n" + "=" * 60)
            logger.info("Sample Job (First Result):")
            logger.info("=" * 60)

            job = jobs[0]
            logger.info(f"Title: {job.title}")
            logger.info(f"Company: {job.company}")
            logger.info(f"Location: {job.location_suburb}, {job.location_state}")
            logger.info(f"Trade: {job.trade}")
            logger.info(f"Employment Type: {job.employment_type}")
            logger.info(f"Pay Range: ${job.pay_range_min} - ${job.pay_range_max}" if job.pay_range_min else "Pay Range: Not specified")
            logger.info(f"Posted At: {job.posted_at}")
            logger.info(f"Job URL: {job.job_url}")
            logger.info(f"Description Preview: {job.description[:200] if job.description else 'N/A'}...")

            logger.info("\n" + "=" * 60)
            logger.info("All Jobs Summary:")
            logger.info("=" * 60)
            for idx, job in enumerate(jobs, 1):
                logger.info(f"{idx}. {job.title} @ {job.company} | Trade: {job.trade} | Location: {job.location_suburb}, {job.location_state}")

        else:
            logger.warning("⚠️  No jobs found")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fastapi_health():
    """测试 FastAPI 健康检查端点"""
    import requests

    logger.info("\n" + "=" * 60)
    logger.info("Testing FastAPI Health Endpoint")
    logger.info("=" * 60)

    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logger.success(f"✅ Health check passed: {data}")
            return True
        else:
            logger.error(f"❌ Health check failed: Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️  Server not running. Please start the server first: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False


def main():
    """主函数"""
    logger.info("🚀 Starting Indeed Adapter Tests\n")

    # Test 1: Adapter 直接测试
    adapter_result = test_indeed_adapter()

    # Test 2: FastAPI 健康检查（如果服务运行中）
    api_result = test_fastapi_health()

    # 总结
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    logger.info(f"Adapter Test: {'✅ PASSED' if adapter_result else '❌ FAILED'}")
    logger.info(f"API Health Check: {'✅ PASSED' if api_result else '⚠️  SKIPPED (server not running)'}")

    if adapter_result:
        logger.success("\n🎉 Indeed adapter is working correctly!")
        logger.info("\nNext steps:")
        logger.info("1. Start the server: uvicorn app.main:app --reload")
        logger.info("2. Visit: http://localhost:8000/docs")
        logger.info("3. Test the /scrape/indeed endpoint with:")
        logger.info('   {"keywords": "tiler", "location": "Adelaide, SA", "max_results": 10}')
    else:
        logger.error("\n❌ Tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()
