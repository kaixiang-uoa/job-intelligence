"""
测试 html_cleaner.py 模块

测试 HTML 清理功能，移除 HTML 标签并保留纯文本
"""

import pytest
from app.utils.html_cleaner import clean_html


def test_clean_html_basic():
    """测试基本的 HTML 清理"""
    html = "<p>This is a test</p>"
    result = clean_html(html)
    assert result == "This is a test"


def test_clean_html_multiple_tags():
    """测试多个标签"""
    html = "<div><p>Hello</p><span>World</span></div>"
    result = clean_html(html)
    assert "Hello" in result
    assert "World" in result
    assert "<" not in result
    assert ">" not in result


def test_clean_html_nested_tags():
    """测试嵌套标签"""
    html = "<div><p><strong>Important</strong> text</p></div>"
    result = clean_html(html)
    assert "Important" in result
    assert "text" in result
    assert "<" not in result


def test_clean_html_with_attributes():
    """测试带属性的标签"""
    html = '<a href="http://example.com" class="link">Click here</a>'
    result = clean_html(html)
    assert result == "Click here"
    assert "href" not in result
    assert "http" not in result


def test_clean_html_with_nbsp():
    """测试 &nbsp; 特殊字符"""
    html = "Hello&nbsp;World"
    result = clean_html(html)
    assert result == "Hello World"


def test_clean_html_with_entities():
    """测试 HTML 实体"""
    html = "A &lt; B &amp; C &gt; D"
    result = clean_html(html)
    assert result == "A < B & C > D"


def test_clean_html_with_quotes():
    """测试引号实体"""
    html = "She said &quot;Hello&quot;"
    result = clean_html(html)
    assert result == 'She said "Hello"'


def test_clean_html_with_linebreaks():
    """测试 <br> 标签转换为换行"""
    html = "Line 1<br>Line 2<br/>Line 3"
    result = clean_html(html)
    assert "Line 1" in result
    assert "Line 2" in result
    assert "Line 3" in result


def test_clean_html_with_paragraphs():
    """测试段落标签"""
    html = "<p>First paragraph</p><p>Second paragraph</p>"
    result = clean_html(html)
    assert "First paragraph" in result
    assert "Second paragraph" in result


def test_clean_html_list():
    """测试列表"""
    html = "<ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>"
    result = clean_html(html)
    assert "Item 1" in result
    assert "Item 2" in result
    assert "Item 3" in result


def test_clean_html_empty():
    """测试空字符串"""
    result = clean_html("")
    assert result == ""


def test_clean_html_none():
    """测试 None 输入"""
    result = clean_html(None)
    assert result is None


def test_clean_html_plain_text():
    """测试纯文本（无 HTML）"""
    text = "This is plain text"
    result = clean_html(text)
    assert result == text


def test_clean_html_whitespace_collapse():
    """测试多余空格的处理"""
    html = "<p>Too    many     spaces</p>"
    result = clean_html(html)
    # 应该折叠多余空格
    assert "  " not in result or result.count("  ") <= 1


def test_clean_html_script_style_removal():
    """测试移除 script 和 style 标签"""
    html = """
    <div>
        <script>alert('hello')</script>
        <style>.class { color: red; }</style>
        <p>Visible text</p>
    </div>
    """
    result = clean_html(html)
    assert "Visible text" in result
    assert "alert" not in result
    assert "color" not in result
    assert "script" not in result


def test_clean_html_complex():
    """测试复杂的真实 HTML"""
    html = """
    <div class="job-description">
        <h3>Job Title</h3>
        <p>We are looking for a <strong>qualified</strong> candidate.</p>
        <ul>
            <li>Requirement 1</li>
            <li>Requirement 2</li>
        </ul>
        <p>Contact us at: <a href="mailto:test@example.com">test@example.com</a></p>
    </div>
    """
    result = clean_html(html)
    assert "Job Title" in result
    assert "qualified" in result
    assert "candidate" in result
    assert "Requirement 1" in result
    assert "Requirement 2" in result
    assert "test@example.com" in result
    assert "<" not in result
    assert ">" not in result
