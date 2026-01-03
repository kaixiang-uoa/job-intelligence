"""
HTML 清理工具

移除 HTML 标签，保留纯文本内容
"""

from typing import Optional
from bs4 import BeautifulSoup
import re


def clean_html(html_str: Optional[str]) -> Optional[str]:
    """
    清理 HTML 字符串，移除标签并保留文本

    Args:
        html_str: HTML 字符串

    Returns:
        str: 清理后的纯文本，如果输入为空则返回 None 或空字符串

    Examples:
        >>> clean_html("<p>Hello World</p>")
        'Hello World'

        >>> clean_html("<strong>Bold</strong> text")
        'Bold text'

        >>> clean_html("Plain text")
        'Plain text'

        >>> clean_html("")
        ''

        >>> clean_html(None)
        None
    """
    # 处理 None
    if html_str is None:
        return None

    # 处理空字符串
    if not html_str:
        return ""

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_str, 'html.parser')

    # 移除 script 和 style 标签（包括其内容）
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()

    # 获取文本
    text = soup.get_text()

    # 替换 non-breaking spaces (\xa0) 为普通空格
    text = text.replace('\xa0', ' ')

    # 清理空格和换行
    # 1. 将多个空格折叠为单个空格
    text = re.sub(r' +', ' ', text)

    # 2. 移除每行首尾空格
    lines = [line.strip() for line in text.splitlines()]

    # 3. 移除空行
    lines = [line for line in lines if line]

    # 4. 用换行符连接
    text = '\n'.join(lines)

    return text.strip()
