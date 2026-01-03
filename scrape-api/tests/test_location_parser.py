"""
测试 location_parser.py 模块

测试地点解析功能，将 "Adelaide, SA" 格式的字符串解析为 (state, suburb) 元组
"""

import pytest
from app.utils.location_parser import parse_location


def test_parse_location_basic():
    """测试基本的地点解析：Adelaide, SA"""
    state, suburb = parse_location("Adelaide, SA")
    assert state == "SA"
    assert suburb == "Adelaide"


def test_parse_location_with_space():
    """测试带空格的郊区名：North Adelaide, SA"""
    state, suburb = parse_location("North Adelaide, SA")
    assert state == "SA"
    assert suburb == "North Adelaide"


def test_parse_location_empty():
    """测试空字符串输入"""
    state, suburb = parse_location("")
    assert state is None
    assert suburb is None


def test_parse_location_invalid():
    """测试无效格式（没有逗号）"""
    state, suburb = parse_location("InvalidFormat")
    assert state is None
    assert suburb is None


def test_parse_location_none():
    """测试 None 输入"""
    state, suburb = parse_location(None)
    assert state is None
    assert suburb is None


def test_parse_location_multiple_commas():
    """测试多个逗号的情况"""
    state, suburb = parse_location("North Adelaide, SA, Australia")
    # 只取前两部分
    assert state == "SA"
    assert suburb == "North Adelaide"


# ========================================
# P1.3 - 复杂格式处理
# ========================================

def test_parse_location_with_ampersand():
    """测试 & 连接的多地点：Toowoomba & Darling Downs QLD"""
    state, suburb = parse_location("Toowoomba & Darling Downs QLD")
    assert state == "QLD"
    assert suburb == "Toowoomba"  # 取第一个地点


def test_parse_location_with_ampersand_comma():
    """测试 & 连接 + 逗号分隔：Toowoomba & Darling Downs, QLD"""
    state, suburb = parse_location("Toowoomba & Darling Downs, QLD")
    assert state == "QLD"
    assert suburb == "Toowoomba"


def test_parse_location_greater_prefix():
    """测试 Greater 前缀：Greater Sydney Area"""
    state, suburb = parse_location("Greater Sydney Area")
    assert state is None  # 没有明确州信息
    assert suburb == "Sydney"  # 提取主要城市名


def test_parse_location_greater_with_state():
    """测试 Greater 前缀 + 州：Greater Sydney, NSW"""
    state, suburb = parse_location("Greater Sydney, NSW")
    assert state == "NSW"
    assert suburb == "Sydney"  # 去掉 Greater 前缀


def test_parse_location_remote():
    """测试 Remote 远程工作：Remote - Australia"""
    state, suburb = parse_location("Remote - Australia")
    assert state == ""  # Remote 没有州
    assert suburb == "Remote"


def test_parse_location_remote_with_state():
    """测试 Remote + 州：Remote, NSW"""
    state, suburb = parse_location("Remote, NSW")
    assert state == "NSW"
    assert suburb == "Remote"


def test_parse_location_all_australia():
    """测试 All Australia：All Australia"""
    state, suburb = parse_location("All Australia")
    assert state == ""  # 全澳大利亚没有特定州
    assert suburb == "All Australia"


def test_parse_location_multiple_regions():
    """测试多地区：Brisbane & Gold Coast, QLD"""
    state, suburb = parse_location("Brisbane & Gold Coast, QLD")
    assert state == "QLD"
    assert suburb == "Brisbane"  # 取第一个地点


def test_parse_location_real_seek_format1():
    """测试真实 SEEK 格式：East Sale, Bairnsdale & Gippsland VIC"""
    state, suburb = parse_location("East Sale, Bairnsdale & Gippsland VIC")
    assert state == "VIC"
    assert suburb == "East Sale"


def test_parse_location_real_seek_format2():
    """测试真实 SEEK 格式：Coolangatta, Gold Coast QLD"""
    state, suburb = parse_location("Coolangatta, Gold Coast QLD")
    assert state == "QLD"
    assert suburb == "Coolangatta"


def test_parse_location_real_seek_format3():
    """测试真实 SEEK 格式：Townsville, Northern QLD"""
    state, suburb = parse_location("Townsville, Northern QLD")
    assert state == "QLD"
    assert suburb == "Townsville"
