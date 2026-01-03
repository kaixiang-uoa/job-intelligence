# TDD 测试驱动开发指南

> **Test-Driven Development (TDD)**
> **核心思想:** 先写测试，再写代码

---

## 🎯 什么是 TDD？

**TDD = Test-Driven Development（测试驱动开发）**

一种**跨语言**的软件开发方法论，要求在编写功能代码**之前**先编写测试代码。

**适用范围：** 所有编程语言（Python, C#, Java, JavaScript, Go, Rust...）

**不是 TTD**（没有这个缩写）

---

## 🔄 TDD 三步循环（Red-Green-Refactor）

```
1. 🔴 RED    → 写一个失败的测试
2. 🟢 GREEN  → 写最少的代码让测试通过
3. 🔵 REFACTOR → 重构代码（保持测试通过）
   ↓
   重复循环
```

### 详细步骤

#### 步骤 1: 🔴 RED（写失败的测试）

**做什么：**
- 写一个测试，定义你想要的功能
- 运行测试，确认它失败（因为功能还没实现）

**为什么失败是好的：**
- 证明测试能检测到问题
- 确保测试不是"总是通过"的假测试

**示例：**
```python
# 测试：解析地点字符串
def test_parse_location():
    state, suburb = parse_location("Adelaide, SA")
    assert state == "SA"
    assert suburb == "Adelaide"

# 运行：❌ FAILED - NameError: parse_location is not defined
```

#### 步骤 2: 🟢 GREEN（让测试通过）

**做什么：**
- 写**最少**的代码让测试通过
- 不用考虑完美，只要通过测试即可

**关键：** 不要过度设计！

**示例：**
```python
# 实现：最简单的版本
def parse_location(location_str: str) -> tuple[str, str]:
    parts = location_str.split(", ")
    suburb = parts[0]
    state = parts[1]
    return state, suburb

# 运行：✅ PASSED
```

#### 步骤 3: 🔵 REFACTOR（重构优化）

**做什么：**
- 优化代码质量
- 消除重复
- 改进可读性
- **保持测试通过**

**示例：**
```python
# 重构：处理边界情况
def parse_location(location_str: str) -> tuple[str, str]:
    """解析地点字符串"""
    if not location_str:
        return None, None

    parts = location_str.split(", ")
    if len(parts) != 2:
        return None, None

    suburb, state = parts[0].strip(), parts[1].strip()
    return state, suburb

# 运行：✅ PASSED（测试依然通过）
```

然后添加新测试继续循环：
```python
# 新测试：处理空字符串
def test_parse_location_empty():
    state, suburb = parse_location("")
    assert state is None
    assert suburb is None

# 🔴 RED → 🟢 GREEN → 🔵 REFACTOR...
```

---

## 💡 TDD 完整示例

### 需求：实现薪资解析函数

**功能：** 将 "$70,000 - $80,000" 解析为 `(70000.0, 80000.0)`

#### 第 1 轮循环

**🔴 RED - 写测试：**
```python
# tests/test_salary_parser.py
def test_parse_salary_range_basic():
    min_sal, max_sal = parse_salary_range("$70,000 - $80,000")
    assert min_sal == 70000.0
    assert max_sal == 80000.0
```

运行：`pytest tests/test_salary_parser.py`
```
❌ FAILED - NameError: name 'parse_salary_range' is not defined
```

**🟢 GREEN - 最小实现：**
```python
# app/utils/salary_parser.py
def parse_salary_range(pay_range: str) -> tuple[float, float]:
    # 硬编码让测试通过（故意的！）
    return 70000.0, 80000.0
```

运行：`pytest`
```
✅ PASSED
```

**🔵 REFACTOR - 真正实现：**
```python
def parse_salary_range(pay_range: str) -> tuple[float, float]:
    import re
    cleaned = pay_range.replace('$', '').replace(',', '')
    numbers = re.findall(r'\d+', cleaned)
    return float(numbers[0]), float(numbers[1])
```

运行：`pytest`
```
✅ PASSED
```

#### 第 2 轮循环

**🔴 RED - 新测试（无范围）：**
```python
def test_parse_salary_range_single():
    min_sal, max_sal = parse_salary_range("$75,000")
    assert min_sal == 75000.0
    assert max_sal == 75000.0  # 单一薪资，min = max
```

运行：`pytest`
```
❌ FAILED - IndexError: list index out of range
```

**🟢 GREEN - 修复：**
```python
def parse_salary_range(pay_range: str) -> tuple[float, float]:
    import re
    cleaned = pay_range.replace('$', '').replace(',', '')
    numbers = re.findall(r'\d+', cleaned)

    if len(numbers) >= 2:
        return float(numbers[0]), float(numbers[1])
    elif len(numbers) == 1:
        amount = float(numbers[0])
        return amount, amount  # 单一薪资
    else:
        return None, None
```

运行：`pytest`
```
✅ 2 passed
```

**🔵 REFACTOR - 添加类型提示和文档：**
```python
from typing import Optional

def parse_salary_range(pay_range: str) -> tuple[Optional[float], Optional[float]]:
    """
    解析薪资范围字符串

    Args:
        pay_range: 薪资字符串，如 "$70,000 - $80,000"

    Returns:
        (最低薪资, 最高薪资) 元组，无法解析时返回 (None, None)
    """
    import re

    cleaned = pay_range.replace('$', '').replace(',', '')
    numbers = re.findall(r'\d+', cleaned)

    if len(numbers) >= 2:
        return float(numbers[0]), float(numbers[1])
    elif len(numbers) == 1:
        amount = float(numbers[0])
        return amount, amount
    else:
        return None, None
```

运行：`pytest`
```
✅ 2 passed
```

---

## ✅ TDD 的好处

| 好处 | 说明 |
|------|------|
| **减少 Bug** | 测试先行，覆盖边界情况 |
| **更好的设计** | 强迫你思考接口和使用方式 |
| **重构安全** | 测试保护，改代码不怕出错 |
| **文档作用** | 测试即文档，展示如何使用 |
| **快速反馈** | 立即知道代码是否正确 |
| **更高信心** | 绿色测试 = 功能正常 |

---

## ❌ TDD 常见误区

### 误区 1: "测试要 100% 覆盖"
**真相：** 重点测试核心逻辑和边界情况，不是每一行代码

### 误区 2: "TDD 会拖慢开发"
**真相：** 初期稍慢，但减少后期调试时间，总体更快

### 误区 3: "要一次写完所有测试"
**真相：** 一次写一个测试，小步快跑

### 误区 4: "GREEN 阶段要写完美代码"
**真相：** GREEN 只求通过，REFACTOR 才优化

---

## 🛠️ TDD 实战技巧

### 1. 测试命名要清晰

**好的命名：**
```python
def test_parse_location_with_comma_separator()
def test_parse_location_with_empty_string()
def test_parse_location_with_invalid_format()
```

**差的命名：**
```python
def test_1()
def test_function()
def test_stuff()
```

### 2. 一次只测试一个行为

**好：**
```python
def test_parse_salary_returns_min():
    min_sal, _ = parse_salary_range("$70,000 - $80,000")
    assert min_sal == 70000.0

def test_parse_salary_returns_max():
    _, max_sal = parse_salary_range("$70,000 - $80,000")
    assert max_sal == 80000.0
```

**差：**
```python
def test_everything():
    # 测试 10 个不同的情况
    assert ...
    assert ...
    assert ...
```

### 3. 使用 AAA 模式

```python
def test_example():
    # Arrange（准备）
    input_data = "Adelaide, SA"

    # Act（执行）
    state, suburb = parse_location(input_data)

    # Assert（断言）
    assert state == "SA"
    assert suburb == "Adelaide"
```

### 4. 测试边界情况

```python
# 正常情况
test_parse_location_normal()

# 边界情况
test_parse_location_empty_string()
test_parse_location_no_comma()
test_parse_location_multiple_commas()
test_parse_location_spaces_only()
test_parse_location_unicode_characters()
```

---

## 📋 TDD 在我们项目中的应用

### 示例：实现 Indeed 适配器

#### 步骤 1: 写测试（🔴 RED）

```python
# tests/test_indeed_adapter.py
import pytest
from app.adapters.indeed_adapter import IndeedAdapter
from app.models.job_posting_dto import ScrapeRequest

def test_indeed_adapter_returns_jobs():
    # Arrange
    adapter = IndeedAdapter()
    request = ScrapeRequest(
        keywords="tiler",
        location="Adelaide",
        max_results=10
    )

    # Act
    jobs = adapter.scrape(request)

    # Assert
    assert len(jobs) > 0
    assert jobs[0].source == "indeed"
    assert jobs[0].title is not None
```

运行：`pytest`
```
❌ FAILED - ModuleNotFoundError: No module named 'indeed_adapter'
```

#### 步骤 2: 最小实现（🟢 GREEN）

```python
# app/adapters/indeed_adapter.py
from app.adapters.base_adapter import BaseJobAdapter
from app.models.job_posting_dto import JobPostingDTO, ScrapeRequest

class IndeedAdapter(BaseJobAdapter):
    @property
    def platform_name(self) -> str:
        return "indeed"

    def scrape(self, request: ScrapeRequest) -> list[JobPostingDTO]:
        # 最小实现：返回一个假数据
        return [
            JobPostingDTO(
                source="indeed",
                source_id="test123",
                title="Test Job",
                company="Test Company"
            )
        ]
```

运行：`pytest`
```
✅ PASSED
```

#### 步骤 3: 真实实现（🔵 REFACTOR）

```python
from jobspy import scrape_jobs

class IndeedAdapter(BaseJobAdapter):
    def scrape(self, request: ScrapeRequest) -> list[JobPostingDTO]:
        # 真实实现：调用 JobSpy
        df = scrape_jobs(
            site_name=['indeed'],
            search_term=request.keywords,
            location=request.location,
            results_wanted=request.max_results,
            country_indeed='Australia'
        )

        jobs = []
        for _, row in df.iterrows():
            job = JobPostingDTO(
                source="indeed",
                source_id=row.get('id') or self._generate_id(row),
                title=row['title'],
                company=row['company'],
                # ... 其他字段
            )
            jobs.append(job)

        return jobs
```

运行：`pytest`
```
✅ PASSED
```

---

## 🎯 TDD vs 传统开发

### 传统开发流程：

```
1. 写代码
2. 手动测试（浏览器点点点）
3. 发现 Bug
4. 改代码
5. 再手动测试
6. （可能）写单元测试
```

### TDD 流程：

```
1. 写测试（定义期望）
2. 运行测试（失败）
3. 写代码（实现功能）
4. 运行测试（通过）
5. 重构（优化代码）
6. 运行测试（确保没破坏）
```

**差异：**
- 传统：代码优先，测试是"额外工作"
- TDD：测试优先，测试是"设计工具"

---

## 📚 TDD 工具推荐（Python）

### pytest - 推荐 ⭐

```bash
pip install pytest pytest-cov

# 运行测试
pytest

# 查看覆盖率
pytest --cov=app tests/

# 监视模式（文件改动自动运行）
pytest-watch
```

### 常用断言

```python
# 相等断言
assert result == expected

# 布尔断言
assert is_valid is True

# 异常断言
with pytest.raises(ValueError):
    parse_salary_range("invalid")

# 近似断言（浮点数）
assert result == pytest.approx(70000.0, rel=0.01)

# 列表包含
assert "tiler" in job.tags

# None 检查
assert job.description is not None
```

---

## 🚀 立即开始 TDD

### 快速启动模板

```python
# tests/test_my_feature.py
import pytest

def test_feature_basic_case():
    """测试基本情况"""
    # Arrange（准备数据）
    input_data = "test input"

    # Act（执行功能）
    result = my_feature(input_data)

    # Assert（验证结果）
    assert result == "expected output"

def test_feature_edge_case():
    """测试边界情况"""
    result = my_feature("")
    assert result is None

def test_feature_raises_error():
    """测试异常情况"""
    with pytest.raises(ValueError):
        my_feature(None)
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_my_feature.py

# 运行特定测试
pytest tests/test_my_feature.py::test_feature_basic_case

# 显示详细输出
pytest -v

# 显示打印语句
pytest -s
```

---

## 📝 总结

### TDD 核心要点

1. **红-绿-重构** 循环：失败 → 通过 → 优化
2. **测试先行**：定义期望行为
3. **小步前进**：一次一个测试
4. **快速反馈**：立即知道对错
5. **重构安全**：测试保护网

### 何时使用 TDD？

**适合 TDD：**
- ✅ 核心业务逻辑（数据转换、计算）
- ✅ 工具函数（解析、格式化）
- ✅ 复杂算法
- ✅ API 端点

**不必 TDD：**
- ❌ 简单的 CRUD 操作
- ❌ UI 布局调整
- ❌ 配置文件
- ❌ 快速原型验证

### 记住

> **TDD 不是教条，而是工具。**
>
> 目标是写出高质量、可维护的代码，
> TDD 是达成目标的方法之一，不是唯一方法。

---

## 🌍 TDD 跨语言通用

### TDD 核心理念与语言无关

**红-绿-重构循环**在所有语言中都一样，只是测试框架不同：

| 语言 | 测试框架 | 示例 |
|------|---------|------|
| **Python** | pytest, unittest | `pytest tests/` |
| **C# / .NET** | xUnit, NUnit, MSTest | `dotnet test` |
| **Java** | JUnit, TestNG | `mvn test` |
| **JavaScript** | Jest, Mocha, Vitest | `npm test` |
| **Go** | testing (内置) | `go test ./...` |
| **Rust** | cargo test (内置) | `cargo test` |
| **Ruby** | RSpec, Minitest | `rspec spec/` |
| **PHP** | PHPUnit | `phpunit` |

### 不同语言的 TDD 示例

#### Python (pytest)
```python
# test_calculator.py
def test_add():
    assert add(2, 3) == 5

# calculator.py
def add(a, b):
    return a + b
```

#### C# (xUnit)
```csharp
// CalculatorTests.cs
public class CalculatorTests
{
    [Fact]
    public void Add_TwoNumbers_ReturnsSum()
    {
        var result = Calculator.Add(2, 3);
        Assert.Equal(5, result);
    }
}

// Calculator.cs
public static class Calculator
{
    public static int Add(int a, int b) => a + b;
}
```

#### JavaScript (Jest)
```javascript
// calculator.test.js
test('add two numbers', () => {
  expect(add(2, 3)).toBe(5);
});

// calculator.js
function add(a, b) {
  return a + b;
}
```

#### Go
```go
// calculator_test.go
func TestAdd(t *testing.T) {
    result := Add(2, 3)
    if result != 5 {
        t.Errorf("Expected 5, got %d", result)
    }
}

// calculator.go
func Add(a, b int) int {
    return a + b
}
```

### 在我们项目中的应用

**本项目同时使用两种语言：**

1. **Python 部分（爬虫服务）**
   - 使用 pytest
   - 测试适配器、工具函数

2. **.NET 部分（后端 API）**
   - 可使用 xUnit 或 NUnit
   - 测试 Controllers、Services、Repositories

**TDD 流程完全一致：**
```
🔴 写测试 → 🟢 实现功能 → 🔵 重构
```

---

## 🔗 推荐阅读

### 通用资源
- **《测试驱动开发》** - Kent Beck（TDD 创始人，跨语言经典）
- **Martin Fowler - TDD** - https://martinfowler.com/bliki/TestDrivenDevelopment.html

### Python 资源
- **pytest 官方文档** - https://docs.pytest.org/
- **Real Python - TDD Tutorial** - https://realpython.com/python-testing/

### .NET 资源
- **xUnit 官方文档** - https://xunit.net/
- **Microsoft - Unit Testing in .NET** - https://learn.microsoft.com/en-us/dotnet/core/testing/

---

**下一步：** 在我们的项目中实践 TDD，从 Indeed 适配器的测试开始！
