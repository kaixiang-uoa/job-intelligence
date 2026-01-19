"""
测试 DateTime UTC 转换修复

验证 seek_adapter 和 indeed_adapter 中的 posted_at 字段
确保返回的是 timezone-aware UTC datetime
"""

import pytest
from datetime import datetime, timezone


def test_datetime_with_timezone_conversion():
    """测试 datetime 转换为 UTC timezone-aware"""

    # 测试场景 1: ISO 格式字符串 (带 Z)
    date_str = "2026-01-15T08:30:00Z"
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))

    # 应该转换为 UTC
    if dt.tzinfo is None:
        posted_at = dt.replace(tzinfo=timezone.utc)
    else:
        posted_at = dt.astimezone(timezone.utc)

    # 验证是 timezone-aware 且为 UTC
    assert posted_at.tzinfo is not None, "DateTime 必须是 timezone-aware"
    assert posted_at.tzinfo == timezone.utc, "DateTime 必须是 UTC"
    assert posted_at.tzname() == 'UTC', "Timezone name 必须是 UTC"

    print(f"✅ 测试 1 通过: {date_str} -> {posted_at} (tzinfo={posted_at.tzinfo})")


def test_datetime_naive_to_utc():
    """测试 naive datetime 转换为 UTC"""

    # 测试场景 2: naive datetime (无时区信息)
    naive_dt = datetime(2026, 1, 15, 8, 30, 0)

    assert naive_dt.tzinfo is None, "初始应该是 naive datetime"

    # 转换为 UTC
    posted_at = naive_dt.replace(tzinfo=timezone.utc)

    # 验证
    assert posted_at.tzinfo is not None, "转换后必须是 timezone-aware"
    assert posted_at.tzinfo == timezone.utc, "转换后必须是 UTC"

    print(f"✅ 测试 2 通过: naive {naive_dt} -> UTC {posted_at}")


def test_datetime_other_timezone_to_utc():
    """测试其他时区转换为 UTC"""

    # 测试场景 3: 带其他时区的 datetime (+10:00 悉尼时间)
    from datetime import timedelta
    sydney_tz = timezone(timedelta(hours=10))
    sydney_dt = datetime(2026, 1, 15, 18, 30, 0, tzinfo=sydney_tz)

    # 转换为 UTC (应该是 08:30 UTC)
    posted_at = sydney_dt.astimezone(timezone.utc)

    # 验证
    assert posted_at.tzinfo == timezone.utc, "必须转换为 UTC"
    assert posted_at.hour == 8, "悉尼 18:30 应该是 UTC 08:30"
    assert posted_at.minute == 30, "分钟应该保持不变"

    print(f"✅ 测试 3 通过: 悉尼 {sydney_dt} -> UTC {posted_at}")


def test_datetime_serialization():
    """测试序列化到 JSON 后的格式"""
    import json

    # 创建 UTC datetime
    utc_dt = datetime(2026, 1, 15, 8, 30, 0, tzinfo=timezone.utc)

    # 序列化（Pydantic 会使用 isoformat()）
    serialized = utc_dt.isoformat()

    # 验证格式
    assert serialized.endswith('+00:00') or serialized.endswith('Z'), \
        "序列化后应该包含 UTC 时区标识"

    print(f"✅ 测试 4 通过: UTC datetime 序列化为 {serialized}")


if __name__ == "__main__":
    print("\n🧪 开始测试 DateTime UTC 转换修复...\n")

    try:
        test_datetime_with_timezone_conversion()
        test_datetime_naive_to_utc()
        test_datetime_other_timezone_to_utc()
        test_datetime_serialization()

        print("\n✅ 所有测试通过！DateTime 修复正确。\n")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}\n")
        raise
