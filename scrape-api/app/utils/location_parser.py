"""
地点解析工具

将 "Adelaide, SA" 格式的字符串解析为 (state, suburb) 元组

P1.3 增强：支持复杂格式
- "Toowoomba & Darling Downs QLD" → ("QLD", "Toowoomba")
- "Greater Sydney, NSW" → ("NSW", "Sydney")
- "Remote - Australia" → ("", "Remote")
"""

import re
from typing import Optional, Tuple


# 澳大利亚州/领地缩写列表
AUSTRALIAN_STATES = {
    "NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"
}


def parse_location(location_str: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    解析地点字符串为 (state, suburb) 元组

    支持多种格式：
    - 基本格式："Adelaide, SA" → ("SA", "Adelaide")
    - 多地点："Toowoomba & Darling Downs, QLD" → ("QLD", "Toowoomba")
    - Greater 前缀："Greater Sydney, NSW" → ("NSW", "Sydney")
    - Remote："Remote - Australia" → ("", "Remote")
    - All Australia："All Australia" → ("", "All Australia")

    Args:
        location_str: 地点字符串

    Returns:
        tuple: (state, suburb)，如果解析失败则返回 (None, None)

        特殊情况：
        - Remote 或 All Australia 返回 ("", suburb)
        - 无法解析返回 (None, None)

    Examples:
        >>> parse_location("Adelaide, SA")
        ('SA', 'Adelaide')

        >>> parse_location("Toowoomba & Darling Downs, QLD")
        ('QLD', 'Toowoomba')

        >>> parse_location("Greater Sydney, NSW")
        ('NSW', 'Sydney')

        >>> parse_location("Remote - Australia")
        ('', 'Remote')
    """
    # 处理 None 和空字符串
    if not location_str:
        return None, None

    location_str = location_str.strip()

    # 特殊情况1: "All Australia"
    if location_str == "All Australia":
        return "", "All Australia"

    # 特殊情况2: "Remote - Australia" 或 "Remote - XXX"（没有逗号的情况）
    if location_str.startswith("Remote") and ", " not in location_str:
        return "", "Remote"

    # 尝试分割逗号（标准格式："Sydney, NSW"）
    if ", " in location_str:
        parts = location_str.split(", ")
        suburb_part = parts[0].strip()
        state_part = parts[1].strip()

        # 处理 state_part 可能包含多个单词的情况（如 "Bairnsdale & Gippsland VIC"）
        # 检查最后一个词是否是州缩写
        state_words = state_part.split()
        if len(state_words) >= 2 and state_words[-1].upper() in AUSTRALIAN_STATES:
            state = state_words[-1].upper()
        else:
            # 如果第二部分本身就是州缩写，直接使用
            state = state_part

        # 处理 & 连接的多地点（取第一个）
        if " & " in suburb_part:
            suburb_part = suburb_part.split(" & ")[0].strip()

        # 处理 Greater 前缀
        suburb_part = _remove_greater_prefix(suburb_part)

        return state, suburb_part

    # 没有逗号，尝试从字符串末尾提取州缩写
    # 例如："Toowoomba & Darling Downs QLD" → 提取 "QLD"
    words = location_str.split()

    # 检查最后一个词是否是州缩写
    if len(words) >= 2 and words[-1].upper() in AUSTRALIAN_STATES:
        state = words[-1].upper()
        suburb_part = " ".join(words[:-1])  # 剩余部分是地点

        # 处理 & 连接的多地点（取第一个）
        if " & " in suburb_part:
            suburb_part = suburb_part.split(" & ")[0].strip()

        # 处理 Greater 前缀
        suburb_part = _remove_greater_prefix(suburb_part)

        return state, suburb_part

    # 没有逗号，也没有明确的州缩写
    # 尝试提取主要地点（处理 "Greater Sydney Area" 这种情况）
    if "Greater " in location_str:
        suburb_part = _remove_greater_prefix(location_str)
        # 移除 "Area" 后缀
        if suburb_part.endswith(" Area"):
            suburb_part = suburb_part[:-5]
        return None, suburb_part

    # 无法解析
    return None, None


def _remove_greater_prefix(location: str) -> str:
    """
    移除 "Greater " 前缀

    Args:
        location: 地点字符串

    Returns:
        str: 移除前缀后的字符串

    Examples:
        >>> _remove_greater_prefix("Greater Sydney")
        'Sydney'

        >>> _remove_greater_prefix("Sydney")
        'Sydney'
    """
    if location.startswith("Greater "):
        return location[8:]  # len("Greater ") == 8
    return location
