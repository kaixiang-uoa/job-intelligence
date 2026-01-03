"""
薪资解析工具

将各种格式的薪资字符串解析为 (min, max) 元组
"""

import re
from typing import Optional, Tuple


# 每周工作小时数（澳大利亚标准）
HOURS_PER_WEEK = 38
# 每年工作周数
WEEKS_PER_YEAR = 52


def parse_salary_range(salary_str: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    """
    解析薪资范围字符串为 (min, max) 元组

    Args:
        salary_str: 薪资字符串

    Returns:
        tuple: (min_salary, max_salary)，无法解析则返回 (None, None)

    Examples:
        >>> parse_salary_range("$70,000 - $80,000")
        (70000.0, 80000.0)

        >>> parse_salary_range("$70k - $80k")
        (70000.0, 80000.0)

        >>> parse_salary_range("$75,000")
        (75000.0, 75000.0)

        >>> parse_salary_range("$35 - $40 per hour")
        (69160.0, 79040.0)

        >>> parse_salary_range("")
        (None, None)
    """
    # 处理 None 和空字符串
    if not salary_str:
        return None, None

    # 去除首尾空格并转换为小写（用于匹配关键词）
    salary_str = salary_str.strip()
    salary_str_lower = salary_str.lower()

    # 检查是否是时薪
    is_hourly = 'hour' in salary_str_lower or '/hour' in salary_str_lower or '/hr' in salary_str_lower

    # 移除常见的文本（per year, per annum, p.a., 等）
    cleaned = re.sub(r'\s*(per\s+(year|annum|hour)|p\.a\.|/hour|/hr)\s*', ' ', salary_str_lower, flags=re.IGNORECASE)

    # 优先检查 "Up to $XX" 或 "From $XX" 的情况
    up_to_match = re.search(r'up\s+to\s+\$?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*([kK])?', cleaned, re.IGNORECASE)
    from_match = re.search(r'from\s+\$?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*([kK])?', cleaned, re.IGNORECASE)

    if up_to_match:
        max_val = _parse_number(up_to_match.group(1), up_to_match.group(2))
        max_val = _convert_hourly_to_annual(max_val, is_hourly)
        return None, max_val
    elif from_match:
        min_val = _parse_number(from_match.group(1), from_match.group(2))
        min_val = _convert_hourly_to_annual(min_val, is_hourly)
        return min_val, None

    # 提取所有数字（支持逗号、k/K 后缀）
    # 匹配模式：可选的 $，数字（可能带逗号），可选的 k/K
    # 修改：支持任意位数的数字（不限制 1-3 位）
    pattern = r'\$?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*([kK])?'
    matches = re.findall(pattern, cleaned)

    if not matches:
        # 无法解析
        return None, None

    # 解析匹配的数字
    numbers = []
    for num_str, k_suffix in matches:
        value = _parse_number(num_str, k_suffix)
        numbers.append(value)

    # 根据匹配数量返回结果
    if len(numbers) == 1:
        # 单一薪资值
        value = _convert_hourly_to_annual(numbers[0], is_hourly)
        return value, value
    elif len(numbers) >= 2:
        # 薪资范围（取前两个）
        min_val = _convert_hourly_to_annual(numbers[0], is_hourly)
        max_val = _convert_hourly_to_annual(numbers[1], is_hourly)
        return min_val, max_val
    else:
        return None, None


def _parse_number(num_str: str, k_suffix: Optional[str]) -> float:
    """
    解析单个数字字符串

    Args:
        num_str: 数字字符串（可能带逗号）
        k_suffix: k/K 后缀

    Returns:
        float: 解析后的数字
    """
    # 移除逗号
    num_str = num_str.replace(',', '')

    # 转换为浮点数
    value = float(num_str)

    # 处理 k/K 后缀（千）
    if k_suffix:
        value *= 1000

    return value


def _convert_hourly_to_annual(value: Optional[float], is_hourly: bool) -> Optional[float]:
    """
    如果是时薪，转换为年薪

    Args:
        value: 薪资值
        is_hourly: 是否是时薪

    Returns:
        float: 转换后的值（如果不是时薪则返回原值）
    """
    if value is None:
        return None

    if is_hourly:
        # 时薪转年薪：时薪 * 每周小时数 * 每年周数
        return value * HOURS_PER_WEEK * WEEKS_PER_YEAR

    return value
