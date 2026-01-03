"""
手动测试 SeekAdapter

测试 SEEK API 调用和数据转换
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.adapters.seek_adapter import SeekAdapter
from app.models.job_posting_dto import ScrapeRequest


def test_seek_adapter():
    """测试 SEEK 适配器"""
    print("=" * 60)
    print("开始测试 SeekAdapter")
    print("=" * 60)

    # 创建适配器
    adapter = SeekAdapter()
    print("\n✅ SeekAdapter 创建成功")

    # 创建请求
    request = ScrapeRequest(
        keywords="plumber",
        location="Sydney NSW",
        max_results=5
    )

    print(f"\n搜索参数:")
    print(f"  - keywords: {request.keywords}")
    print(f"  - location: {request.location}")
    print(f"  - max_results: {request.max_results}")

    try:
        # 调用 scrape
        print("\n📡 调用 SEEK API...")
        jobs = adapter.scrape(request)

        # 显示结果
        print(f"\n✅ 成功抓取 {len(jobs)} 个职位\n")

        # 显示每个职位的详细信息
        for i, job in enumerate(jobs, 1):
            print(f"职位 {i}:")
            print(f"  来源: {job.source}")
            print(f"  ID: {job.source_id}")
            print(f"  标题: {job.title}")
            print(f"  公司: {job.company}")
            print(f"  地点: {job.location_suburb}, {job.location_state}")
            print(f"  薪资: ${job.pay_range_min} - ${job.pay_range_max}")
            print(f"  类型: {job.employment_type}")
            print(f"  Trade: {job.trade}")
            print(f"  描述: {job.description[:100] if job.description else 'N/A'}...")
            print(f"  URL: {job.job_url}")
            print(f"  发布时间: {job.posted_at}")
            print(f"  爬取时间: {job.scraped_at}")
            print()

        print("=" * 60)
        print("✅ 测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_seek_adapter()
