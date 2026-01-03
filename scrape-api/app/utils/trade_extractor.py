"""
Trade 提取工具

从职位标题中提取 trade 类型（如 tiler, plumber, electrician 等）
"""

from typing import Optional


# Trade 关键词映射表
TRADE_KEYWORDS = {
    'tiler': ['tiler', 'tiling'],
    'plumber': ['plumber', 'plumbing'],
    'electrician': ['electrician', 'electrical', 'sparky'],
    'bricklayer': ['bricklayer', 'brick', 'mason'],
    'carpenter': ['carpenter', 'carpentry'],
    'painter': ['painter', 'painting'],
    'roofer': ['roofer', 'roofing'],
    'welder': ['welder', 'welding'],
    'glazier': ['glazier', 'glazing', 'glass'],
    'plasterer': ['plasterer', 'plastering'],
    'concreter': ['concreter', 'concreting', 'concrete'],
    'stonemason': ['stonemason', 'stone mason'],
    'scaffolder': ['scaffolder', 'scaffolding'],
}


def extract_trade(title: Optional[str]) -> Optional[str]:
    """
    从职位标题中提取 trade 类型

    Args:
        title: 职位标题字符串

    Returns:
        str: 识别的 trade 类型（小写），如果无法识别则返回 None

    Examples:
        >>> extract_trade("Experienced Tiler - Adelaide")
        'tiler'

        >>> extract_trade("Qualified Plumber Needed")
        'plumber'

        >>> extract_trade("Electrician - Full Time")
        'electrician'

        >>> extract_trade("Looking for a Sparky")
        'electrician'

        >>> extract_trade("Office Manager")
        None
    """
    # 处理 None 和空字符串
    if not title:
        return None

    # 转换为小写进行匹配
    title_lower = title.lower()

    # 遍历所有 trade 及其关键词
    for trade, keywords in TRADE_KEYWORDS.items():
        # 检查标题中是否包含任何关键词
        for keyword in keywords:
            if keyword in title_lower:
                return trade

    # 没有匹配到任何 trade
    return None
