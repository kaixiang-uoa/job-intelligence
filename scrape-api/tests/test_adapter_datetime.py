"""
测试适配器中的 DateTime 处理

模拟 seek 和 indeed adapter 的 posted_at 解析逻辑
"""

from datetime import datetime, timezone


def test_seek_adapter_datetime_parsing():
    """模拟 SEEK adapter 的 posted_at 解析"""
    print("\n🧪 测试 SEEK adapter datetime 解析...")

    # SEEK API 返回的日期格式示例
    test_cases = [
        "2026-01-15T08:30:00Z",
        "2026-01-15T08:30:00+00:00",
        "2026-01-15T18:30:00+10:00",  # 悉尼时间
    ]

    for created_at in test_cases:
        # 模拟 seek_adapter.py 的解析逻辑
        if isinstance(created_at, str):
            try:
                # 解析 ISO 格式时间字符串并转换为 UTC
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                # 确保是 timezone-aware 且为 UTC
                if dt.tzinfo is None:
                    posted_at = dt.replace(tzinfo=timezone.utc)
                else:
                    # 转换到 UTC
                    posted_at = dt.astimezone(timezone.utc)

                # 验证
                assert posted_at.tzinfo is not None, f"Failed for {created_at}: not timezone-aware"
                assert posted_at.tzinfo == timezone.utc, f"Failed for {created_at}: not UTC"

                print(f"  ✅ {created_at:35s} -> {posted_at} (UTC)")

            except ValueError as e:
                print(f"  ❌ 解析失败: {created_at} - {e}")
                raise


def test_indeed_adapter_datetime_parsing():
    """模拟 Indeed adapter 的 date_posted 解析"""
    print("\n🧪 测试 Indeed adapter datetime 解析...")

    # Indeed/JobSpy 返回的日期格式
    test_cases = [
        "2026-01-15T08:30:00Z",
        "2026-01-15T08:30:00+00:00",
        datetime(2026, 1, 15, 8, 30, 0),  # naive datetime
        datetime(2026, 1, 15, 8, 30, 0, tzinfo=timezone.utc),  # UTC datetime
    ]

    for date_posted in test_cases:
        # 模拟 indeed_adapter.py 的解析逻辑
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

                # 验证
                assert posted_at.tzinfo is not None, f"Failed for {date_posted}: not timezone-aware"
                assert posted_at.tzinfo == timezone.utc, f"Failed for {date_posted}: not UTC"

                print(f"  ✅ {str(date_posted):35s} -> {posted_at} (UTC)")

            except Exception as e:
                print(f"  ❌ 解析失败: {date_posted} - {e}")
                raise


def test_pydantic_serialization():
    """测试 Pydantic 序列化（确保能传递给 .NET）"""
    print("\n🧪 测试 Pydantic 序列化...")

    from pydantic import BaseModel

    class TestModel(BaseModel):
        posted_at: datetime

    # 创建 UTC datetime
    utc_dt = datetime(2026, 1, 15, 8, 30, 0, tzinfo=timezone.utc)

    model = TestModel(posted_at=utc_dt)

    # 序列化为 JSON
    json_data = model.model_dump_json()

    print(f"  ✅ 序列化结果: {json_data}")

    # 验证包含时区信息
    assert '+00:00' in json_data or 'Z' in json_data, "序列化后应包含 UTC 时区标识"


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  测试适配器 DateTime 处理")
    print("="*60)

    try:
        test_seek_adapter_datetime_parsing()
        test_indeed_adapter_datetime_parsing()
        test_pydantic_serialization()

        print("\n" + "="*60)
        print("  ✅ 所有适配器测试通过！")
        print("="*60 + "\n")

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}\n")
        raise
