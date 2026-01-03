"""
测试 employment_type.py 模块

测试工作类型标准化功能
"""

import pytest
from app.utils.employment_type import normalize_employment_type


def test_normalize_fulltime():
    """测试 fulltime → Full Time"""
    result = normalize_employment_type("fulltime")
    assert result == "Full Time"


def test_normalize_fulltime_with_dash():
    """测试 full-time → Full Time"""
    result = normalize_employment_type("full-time")
    assert result == "Full Time"


def test_normalize_parttime():
    """测试 parttime → Part Time"""
    result = normalize_employment_type("parttime")
    assert result == "Part Time"


def test_normalize_parttime_with_dash():
    """测试 part-time → Part Time"""
    result = normalize_employment_type("part-time")
    assert result == "Part Time"


def test_normalize_contract():
    """测试 contract → Contract"""
    result = normalize_employment_type("contract")
    assert result == "Contract"


def test_normalize_casual():
    """测试 casual → Casual"""
    result = normalize_employment_type("casual")
    assert result == "Casual"


def test_normalize_temporary():
    """测试 temporary → Temporary"""
    result = normalize_employment_type("temporary")
    assert result == "Temporary"


def test_normalize_already_normalized():
    """测试已经标准化的输入"""
    result = normalize_employment_type("Full Time")
    assert result == "Full Time"


def test_normalize_with_spaces():
    """测试带前后空格的输入"""
    result = normalize_employment_type("  fulltime  ")
    assert result == "Full Time"


def test_normalize_case_insensitive():
    """测试大小写不敏感"""
    result = normalize_employment_type("FULLTIME")
    assert result == "Full Time"


def test_normalize_none():
    """测试 None 输入"""
    result = normalize_employment_type(None)
    assert result is None


def test_normalize_empty():
    """测试空字符串"""
    result = normalize_employment_type("")
    assert result is None


def test_normalize_unknown():
    """测试未知类型（保持原样）"""
    result = normalize_employment_type("Unknown Type")
    assert result == "Unknown Type"


def test_normalize_mixed_case():
    """测试混合大小写"""
    result = normalize_employment_type("FullTime")
    assert result == "Full Time"
