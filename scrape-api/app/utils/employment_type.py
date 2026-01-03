"""
工作类型标准化工具

将各种格式的工作类型标准化为统一格式
"""

from typing import Optional


# 工作类型映射表
EMPLOYMENT_TYPE_MAPPING = {
    'fulltime': 'Full Time',
    'full-time': 'Full Time',
    'full time': 'Full Time',
    'ft': 'Full Time',

    'parttime': 'Part Time',
    'part-time': 'Part Time',
    'part time': 'Part Time',
    'pt': 'Part Time',

    'contract': 'Contract',
    'contractor': 'Contract',

    'casual': 'Casual',

    'temporary': 'Temporary',
    'temp': 'Temporary',

    'permanent': 'Permanent',

    'internship': 'Internship',
    'intern': 'Internship',
}


def normalize_employment_type(employment_type: Optional[str]) -> Optional[str]:
    """
    标准化工作类型

    Args:
        employment_type: 原始工作类型字符串

    Returns:
        str: 标准化后的工作类型，如果无法识别则返回原值，如果为空则返回 None

    Examples:
        >>> normalize_employment_type("fulltime")
        'Full Time'

        >>> normalize_employment_type("part-time")
        'Part Time'

        >>> normalize_employment_type("contract")
        'Contract'

        >>> normalize_employment_type("Full Time")
        'Full Time'

        >>> normalize_employment_type("Unknown Type")
        'Unknown Type'

        >>> normalize_employment_type("")
        None
    """
    # 处理 None 和空字符串
    if not employment_type:
        return None

    # 转换为小写并去除首尾空格
    normalized = employment_type.lower().strip()

    # 如果为空字符串，返回 None
    if not normalized:
        return None

    # 查找映射表
    if normalized in EMPLOYMENT_TYPE_MAPPING:
        return EMPLOYMENT_TYPE_MAPPING[normalized]

    # 如果没有找到映射，返回原值（保持原格式）
    return employment_type
