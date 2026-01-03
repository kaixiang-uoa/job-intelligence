#!/usr/bin/env python3
"""
MVP 数据分析脚本

用途：
1. 连接数据库获取统计数据
2. 生成可视化报告（文本格式）
3. 导出数据到 JSON/CSV

使用：
    python3 analyze_data.py
    python3 analyze_data.py --export json
    python3 analyze_data.py --export csv
"""

import psycopg2
import json
import csv
from datetime import datetime
from collections import defaultdict
import argparse


# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "jobintel",
    "user": "admin",
    "password": "dev123"
}


def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(**DB_CONFIG)


def get_basic_stats(conn):
    """获取基础统计数据"""
    cur = conn.cursor()

    stats = {}

    # 总职位数
    cur.execute("SELECT COUNT(*) FROM job_postings")
    stats['total_jobs'] = cur.fetchone()[0]

    # 活跃职位数
    cur.execute("SELECT COUNT(*) FROM job_postings WHERE is_active = true")
    stats['active_jobs'] = cur.fetchone()[0]

    # 按来源统计
    cur.execute("""
        SELECT source, COUNT(*)
        FROM job_postings
        GROUP BY source
    """)
    stats['by_source'] = dict(cur.fetchall())

    # 按 trade 统计
    cur.execute("""
        SELECT
            COALESCE(trade, 'NULL') as trade,
            COUNT(*)
        FROM job_postings
        GROUP BY trade
        ORDER BY COUNT(*) DESC
    """)
    stats['by_trade'] = dict(cur.fetchall())

    # 按州统计
    cur.execute("""
        SELECT
            COALESCE(location_state, 'NULL') as state,
            COUNT(*)
        FROM job_postings
        GROUP BY location_state
        ORDER BY COUNT(*) DESC
    """)
    stats['by_state'] = dict(cur.fetchall())

    cur.close()
    return stats


def check_data_quality(conn):
    """检查数据质量"""
    cur = conn.cursor()

    quality = {}

    # 去重检查
    cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT source_id, COUNT(*)
            FROM job_postings
            GROUP BY source_id
            HAVING COUNT(*) > 1
        ) duplicates
    """)
    quality['duplicate_count'] = cur.fetchone()[0]

    # Trade 提取成功率
    cur.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(trade) as with_trade
        FROM job_postings
    """)
    row = cur.fetchone()
    quality['trade_extraction_rate'] = round(100.0 * row[1] / row[0], 2) if row[0] > 0 else 0

    # Location 提取成功率
    cur.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(location_state) as with_location
        FROM job_postings
    """)
    row = cur.fetchone()
    quality['location_extraction_rate'] = round(100.0 * row[1] / row[0], 2) if row[0] > 0 else 0

    # 薪资数据完整性
    cur.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(pay_range_min) as with_salary
        FROM job_postings
    """)
    row = cur.fetchone()
    quality['salary_data_rate'] = round(100.0 * row[1] / row[0], 2) if row[0] > 0 else 0

    # 计算整体质量评分
    dedup_score = 100 if quality['duplicate_count'] == 0 else 80
    quality['overall_score'] = round(
        (dedup_score + quality['trade_extraction_rate'] + quality['location_extraction_rate']) / 3,
        2
    )

    cur.close()
    return quality


def get_recent_jobs(conn, limit=10):
    """获取最近的职位"""
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            title,
            company,
            location_state,
            location_suburb,
            trade,
            employment_type,
            pay_range_min,
            pay_range_max,
            posted_at,
            source
        FROM job_postings
        ORDER BY posted_at DESC
        LIMIT %s
    """, (limit,))

    columns = [desc[0] for desc in cur.description]
    jobs = []
    for row in cur.fetchall():
        job = dict(zip(columns, row))
        # 转换日期为字符串
        if job['posted_at']:
            job['posted_at'] = job['posted_at'].isoformat()
        jobs.append(job)

    cur.close()
    return jobs


def print_report(stats, quality, recent_jobs):
    """打印文本报告"""
    print("=" * 60)
    print("📊 Job Intelligence MVP - 数据分析报告")
    print("=" * 60)
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 基础统计
    print("1️⃣ 基础统计")
    print("-" * 60)
    print(f"总职位数: {stats['total_jobs']}")
    print(f"活跃职位数: {stats['active_jobs']}")
    print()

    # 按来源分布
    print("2️⃣ 数据来源分布")
    print("-" * 60)
    for source, count in stats['by_source'].items():
        percentage = round(100.0 * count / stats['total_jobs'], 2)
        print(f"{source:10s}: {count:5d} ({percentage:5.2f}%)")
    print()

    # 按 Trade 分布（Top 10）
    print("3️⃣ Trade 分布（Top 10）")
    print("-" * 60)
    for i, (trade, count) in enumerate(list(stats['by_trade'].items())[:10], 1):
        print(f"{i:2d}. {trade:20s}: {count:4d}")
    print()

    # 按州分布
    print("4️⃣ 地点分布（按州）")
    print("-" * 60)
    for state, count in stats['by_state'].items():
        percentage = round(100.0 * count / stats['total_jobs'], 2)
        print(f"{state:5s}: {count:5d} ({percentage:5.2f}%)")
    print()

    # 数据质量
    print("5️⃣ 数据质量评估")
    print("-" * 60)
    print(f"重复数据: {quality['duplicate_count']} 个")
    print(f"Trade 提取成功率: {quality['trade_extraction_rate']}%")
    print(f"地点提取成功率: {quality['location_extraction_rate']}%")
    print(f"薪资数据完整性: {quality['salary_data_rate']}%")
    print()
    print(f"整体质量评分: {quality['overall_score']}/100")

    if quality['overall_score'] >= 95:
        print("✅ 优秀！数据质量达到生产标准")
    elif quality['overall_score'] >= 80:
        print("⚠️  良好，但仍有优化空间")
    else:
        print("❌ 数据质量需要改进")
    print()

    # 最近职位预览
    print("6️⃣ 最近职位预览（最新 10 条）")
    print("-" * 60)
    for i, job in enumerate(recent_jobs, 1):
        title = job['title'][:40] + '...' if len(job['title']) > 40 else job['title']
        print(f"{i:2d}. {title}")
        print(f"    公司: {job['company'] or 'N/A'} | 州: {job['location_state'] or 'N/A'} | Trade: {job['trade'] or 'N/A'}")
    print()

    print("=" * 60)
    print("✅ 分析完成")
    print("=" * 60)


def export_to_json(stats, quality, recent_jobs, filename="data_analysis.json"):
    """导出为 JSON"""
    data = {
        "generated_at": datetime.now().isoformat(),
        "statistics": stats,
        "quality": quality,
        "recent_jobs": recent_jobs
    }

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ 数据已导出到: {filename}")


def export_to_csv(recent_jobs, filename="recent_jobs.csv"):
    """导出为 CSV"""
    if not recent_jobs:
        print("⚠️  没有数据可导出")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=recent_jobs[0].keys())
        writer.writeheader()
        writer.writerows(recent_jobs)

    print(f"✅ 职位数据已导出到: {filename}")


def main():
    parser = argparse.ArgumentParser(description='MVP 数据分析脚本')
    parser.add_argument('--export', choices=['json', 'csv', 'both'],
                        help='导出格式 (json/csv/both)')
    args = parser.parse_args()

    try:
        # 连接数据库
        conn = get_db_connection()

        # 获取数据
        stats = get_basic_stats(conn)
        quality = check_data_quality(conn)
        recent_jobs = get_recent_jobs(conn, limit=10)

        # 打印报告
        print_report(stats, quality, recent_jobs)

        # 导出数据
        if args.export in ['json', 'both']:
            export_to_json(stats, quality, recent_jobs)

        if args.export in ['csv', 'both']:
            export_to_csv(recent_jobs)

        conn.close()

    except psycopg2.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()
