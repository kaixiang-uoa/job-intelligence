"""
测试 salary_parser.py 模块

测试薪资范围解析功能，将各种格式的薪资字符串解析为 (min, max) 元组
"""

import pytest
from app.utils.salary_parser import parse_salary_range


def test_parse_salary_range_basic():
    """测试基本的薪资范围：$70,000 - $80,000"""
    min_salary, max_salary = parse_salary_range("$70,000 - $80,000")
    assert min_salary == 70000.0
    assert max_salary == 80000.0


def test_parse_salary_range_no_commas():
    """测试没有千位分隔符：$70000 - $80000"""
    min_salary, max_salary = parse_salary_range("$70000 - $80000")
    assert min_salary == 70000.0
    assert max_salary == 80000.0


def test_parse_salary_range_k_suffix():
    """测试 k 后缀：$70k - $80k"""
    min_salary, max_salary = parse_salary_range("$70k - $80k")
    assert min_salary == 70000.0
    assert max_salary == 80000.0


def test_parse_salary_range_K_suffix():
    """测试大写 K 后缀：$70K - $80K"""
    min_salary, max_salary = parse_salary_range("$70K - $80K")
    assert min_salary == 70000.0
    assert max_salary == 80000.0


def test_parse_salary_range_mixed_format():
    """测试混合格式：$70,000 - $80k"""
    min_salary, max_salary = parse_salary_range("$70,000 - $80k")
    assert min_salary == 70000.0
    assert max_salary == 80000.0


def test_parse_salary_range_single_value():
    """测试单一薪资值：$75,000"""
    min_salary, max_salary = parse_salary_range("$75,000")
    assert min_salary == 75000.0
    assert max_salary == 75000.0


def test_parse_salary_range_no_dollar_sign():
    """测试没有美元符号：70000 - 80000"""
    min_salary, max_salary = parse_salary_range("70000 - 80000")
    assert min_salary == 70000.0
    assert max_salary == 80000.0


def test_parse_salary_range_with_to():
    """测试使用 'to' 分隔：$70,000 to $80,000"""
    min_salary, max_salary = parse_salary_range("$70,000 to $80,000")
    assert min_salary == 70000.0
    assert max_salary == 80000.0


def test_parse_salary_range_per_year():
    """测试带 per year：$70,000 - $80,000 per year"""
    min_salary, max_salary = parse_salary_range("$70,000 - $80,000 per year")
    assert min_salary == 70000.0
    assert max_salary == 80000.0


def test_parse_salary_range_hourly():
    """测试时薪（按年计算）：$35 - $40 per hour"""
    min_salary, max_salary = parse_salary_range("$35 - $40 per hour")
    # 假设每周工作 38 小时，每年 52 周
    # $35/hour * 38 hours/week * 52 weeks/year = $69,160
    # $40/hour * 38 hours/week * 52 weeks/year = $79,040
    assert min_salary == pytest.approx(69160.0, rel=1)
    assert max_salary == pytest.approx(79040.0, rel=1)


def test_parse_salary_range_hourly_single():
    """测试单一时薪：$35/hour"""
    min_salary, max_salary = parse_salary_range("$35/hour")
    # $35/hour * 38 * 52 = $69,160
    assert min_salary == pytest.approx(69160.0, rel=1)
    assert max_salary == pytest.approx(69160.0, rel=1)


def test_parse_salary_range_empty():
    """测试空字符串"""
    min_salary, max_salary = parse_salary_range("")
    assert min_salary is None
    assert max_salary is None


def test_parse_salary_range_none():
    """测试 None 输入"""
    min_salary, max_salary = parse_salary_range(None)
    assert min_salary is None
    assert max_salary is None


def test_parse_salary_range_invalid():
    """测试无效格式"""
    min_salary, max_salary = parse_salary_range("Negotiable")
    assert min_salary is None
    assert max_salary is None


def test_parse_salary_range_with_whitespace():
    """测试带额外空格：  $70,000  -  $80,000  """
    min_salary, max_salary = parse_salary_range("  $70,000  -  $80,000  ")
    assert min_salary == 70000.0
    assert max_salary == 80000.0


def test_parse_salary_range_only_max():
    """测试只有最大值：Up to $80,000"""
    min_salary, max_salary = parse_salary_range("Up to $80,000")
    assert min_salary is None
    assert max_salary == 80000.0


def test_parse_salary_range_only_min():
    """测试只有最小值：From $70,000"""
    min_salary, max_salary = parse_salary_range("From $70,000")
    assert min_salary == 70000.0
    assert max_salary is None
