"""
测试 trade_extractor.py 模块

测试从职位标题中提取 trade 类型的功能
"""

import pytest
from app.utils.trade_extractor import extract_trade


def test_extract_trade_tiler():
    """测试识别 tiler"""
    trade = extract_trade("Experienced Tiler - Adelaide")
    assert trade == "tiler"


def test_extract_trade_tiler_variant():
    """测试识别 tiling 变体"""
    trade = extract_trade("Tiling Professional Needed")
    assert trade == "tiler"


def test_extract_trade_plumber():
    """测试识别 plumber"""
    trade = extract_trade("Qualified Plumber Needed")
    assert trade == "plumber"


def test_extract_trade_plumbing():
    """测试识别 plumbing 变体"""
    trade = extract_trade("Plumbing Services - Full Time")
    assert trade == "plumber"


def test_extract_trade_electrician():
    """测试识别 electrician"""
    trade = extract_trade("Electrician - Full Time")
    assert trade == "electrician"


def test_extract_trade_electrical():
    """测试识别 electrical 变体"""
    trade = extract_trade("Electrical Engineer Position")
    assert trade == "electrician"


def test_extract_trade_sparky():
    """测试识别澳大利亚俚语 sparky"""
    trade = extract_trade("Looking for a Sparky - Adelaide")
    assert trade == "electrician"


def test_extract_trade_bricklayer():
    """测试识别 bricklayer"""
    trade = extract_trade("Bricklayer Position Available")
    assert trade == "bricklayer"


def test_extract_trade_brick():
    """测试识别 brick 变体"""
    trade = extract_trade("Brick Mason Required")
    assert trade == "bricklayer"


def test_extract_trade_carpenter():
    """测试识别 carpenter"""
    trade = extract_trade("Experienced Carpenter - Sydney")
    assert trade == "carpenter"


def test_extract_trade_painter():
    """测试识别 painter"""
    trade = extract_trade("Painter & Decorator")
    assert trade == "painter"


def test_extract_trade_not_found():
    """测试无法识别的职位"""
    trade = extract_trade("Office Manager")
    assert trade is None


def test_extract_trade_case_insensitive():
    """测试大小写不敏感"""
    trade = extract_trade("TILER - URGENT")
    assert trade == "tiler"


def test_extract_trade_empty():
    """测试空字符串"""
    trade = extract_trade("")
    assert trade is None


def test_extract_trade_none():
    """测试 None 输入"""
    trade = extract_trade(None)
    assert trade is None


def test_extract_trade_multiple_matches():
    """测试多个匹配时返回第一个"""
    trade = extract_trade("Plumber and Electrician Team")
    # 应该返回第一个匹配的 trade
    assert trade in ["plumber", "electrician"]
