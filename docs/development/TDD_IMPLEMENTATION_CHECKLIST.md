# TDD 实施检查清单

> **用途:** 阶段 2 开发时的逐步检查清单
> **方法:** 渐进式 TDD（工具函数完全 TDD，适配器混合方式）

---

## 📋 使用说明

**本清单按照执行顺序排列，逐项完成并打勾 ✅**

每个函数严格遵循：**🔴 RED → 🟢 GREEN → 🔵 REFACTOR**

---

## Phase 2.1: 工具函数（完全 TDD）

### 🎯 函数 1: parse_location() - 地点解析

#### 🔴 RED 阶段（写失败的测试）

- [ ] 创建测试文件 `tests/test_location_parser.py`
- [ ] 编写测试：`test_parse_location_basic()`
  ```python
  def test_parse_location_basic():
      state, suburb = parse_location("Adelaide, SA")
      assert state == "SA"
      assert suburb == "Adelaide"
  ```
- [ ] 运行 `pytest tests/test_location_parser.py`
- [ ] 确认失败：`❌ NameError: name 'parse_location' is not defined`

- [ ] 编写测试：`test_parse_location_with_space()`
  ```python
  def test_parse_location_with_space():
      state, suburb = parse_location("North Adelaide, SA")
      assert state == "SA"
      assert suburb == "North Adelaide"
  ```

- [ ] 编写测试：`test_parse_location_empty()`
  ```python
  def test_parse_location_empty():
      state, suburb = parse_location("")
      assert state is None
      assert suburb is None
  ```

- [ ] 编写测试：`test_parse_location_invalid()`
  ```python
  def test_parse_location_invalid():
      state, suburb = parse_location("InvalidFormat")
      assert state is None
      assert suburb is None
  ```

#### 🟢 GREEN 阶段（让测试通过）

- [ ] 创建文件 `app/utils/location_parser.py`
- [ ] 实现最简单的版本（只让第一个测试通过）
  ```python
  def parse_location(location_str: str):
      parts = location_str.split(", ")
      return parts[1], parts[0]
  ```
- [ ] 运行 `pytest tests/test_location_parser.py::test_parse_location_basic`
- [ ] 确认通过：`✅ 1 passed`

- [ ] 运行所有测试 `pytest tests/test_location_parser.py`
- [ ] 逐个修复失败的测试（处理边界情况）
- [ ] 确认全部通过：`✅ 4 passed`

#### 🔵 REFACTOR 阶段（重构优化）

- [ ] 添加类型注解
  ```python
  from typing import Optional, Tuple

  def parse_location(location_str: str) -> Tuple[Optional[str], Optional[str]]:
  ```
- [ ] 添加文档字符串
- [ ] 优化代码逻辑（去除重复、提高可读性）
- [ ] 运行测试确认仍然通过：`pytest tests/test_location_parser.py`
- [ ] 确认：`✅ 4 passed`

---

### 🎯 函数 2: extract_trade() - Trade 提取

#### 🔴 RED 阶段

- [ ] 创建测试文件 `tests/test_trade_extractor.py`
- [ ] 编写测试：`test_extract_trade_tiler()`
  ```python
  def test_extract_trade_tiler():
      trade = extract_trade("Experienced Tiler - Adelaide")
      assert trade == "tiler"
  ```
- [ ] 运行测试，确认失败

- [ ] 编写测试：`test_extract_trade_plumber()`
  ```python
  def test_extract_trade_plumber():
      trade = extract_trade("Qualified Plumber Needed")
      assert trade == "plumber"
  ```

- [ ] 编写测试：`test_extract_trade_electrician()`
  ```python
  def test_extract_trade_electrician():
      trade = extract_trade("Electrician - Full Time")
      assert trade == "electrician"
  ```

- [ ] 编写测试：`test_extract_trade_bricklayer()`
  ```python
  def test_extract_trade_bricklayer():
      trade = extract_trade("Bricklayer Position Available")
      assert trade == "bricklayer"
  ```

- [ ] 编写测试：`test_extract_trade_not_found()`
  ```python
  def test_extract_trade_not_found():
      trade = extract_trade("Office Manager")
      assert trade is None
  ```

#### 🟢 GREEN 阶段

- [ ] 创建文件 `app/utils/trade_extractor.py`
- [ ] 定义 Trade 关键词字典
  ```python
  TRADE_KEYWORDS = {
      'tiler': ['tiler', 'tiling'],
      'plumber': ['plumber', 'plumbing'],
      'electrician': ['electrician', 'electrical', 'sparky'],
      'bricklayer': ['bricklayer', 'brick'],
      # ... 更多
  }
  ```
- [ ] 实现 `extract_trade()` 函数
- [ ] 运行测试：`pytest tests/test_trade_extractor.py`
- [ ] 确认全部通过：`✅ 5 passed`

#### 🔵 REFACTOR 阶段

- [ ] 添加类型注解
- [ ] 添加文档字符串
- [ ] 优化关键词匹配逻辑
- [ ] 运行测试确认通过

---

### 🎯 函数 3: normalize_employment_type() - 工作类型标准化

#### 🔴 RED 阶段

- [ ] 创建测试文件 `tests/test_employment_type.py`
- [ ] 编写测试：`test_normalize_fulltime()`
  ```python
  def test_normalize_fulltime():
      result = normalize_employment_type("fulltime")
      assert result == "Full Time"
  ```
- [ ] 编写测试：`test_normalize_parttime()`
- [ ] 编写测试：`test_normalize_contract()`
- [ ] 编写测试：`test_normalize_already_normalized()`
  ```python
  def test_normalize_already_normalized():
      result = normalize_employment_type("Full Time")
      assert result == "Full Time"
  ```
- [ ] 编写测试：`test_normalize_none()`
  ```python
  def test_normalize_none():
      result = normalize_employment_type(None)
      assert result is None
  ```

#### 🟢 GREEN 阶段

- [ ] 创建文件 `app/utils/employment_type.py`
- [ ] 定义映射字典
  ```python
  EMPLOYMENT_TYPE_MAPPING = {
      'fulltime': 'Full Time',
      'parttime': 'Part Time',
      'contract': 'Contract',
      # ...
  }
  ```
- [ ] 实现 `normalize_employment_type()` 函数
- [ ] 运行测试：`pytest tests/test_employment_type.py`
- [ ] 确认通过：`✅ 5 passed`

#### 🔵 REFACTOR 阶段

- [ ] 添加类型注解
- [ ] 添加文档字符串
- [ ] 运行测试确认通过

---

## Phase 2.2: Indeed 适配器（混合方式）

### 🚀 先实现，后补测试

- [ ] 创建文件 `app/adapters/indeed_adapter.py`
- [ ] 实现 `IndeedAdapter` 类
  ```python
  from app.adapters.base_adapter import BaseJobAdapter
  from jobspy import scrape_jobs

  class IndeedAdapter(BaseJobAdapter):
      @property
      def platform_name(self) -> str:
          return "indeed"

      def scrape(self, request: ScrapeRequest) -> List[JobPostingDTO]:
          # 实现逻辑
          pass
  ```

- [ ] 集成 JobSpy 库
  ```python
  df = scrape_jobs(
      site_name=['indeed'],
      search_term=request.keywords,
      location=request.location,
      results_wanted=request.max_results,
      country_indeed='Australia'
  )
  ```

- [ ] 实现数据转换逻辑
  ```python
  from app.utils.location_parser import parse_location
  from app.utils.trade_extractor import extract_trade

  for _, row in df.iterrows():
      state, suburb = parse_location(row['location'])
      trade = extract_trade(row['title'])
      # ... 转换为 JobPostingDTO
  ```

- [ ] 手动测试（创建临时测试脚本）
  ```python
  # test_manual.py
  adapter = IndeedAdapter()
  request = ScrapeRequest(keywords="tiler", location="Adelaide", max_results=10)
  jobs = adapter.scrape(request)
  print(f"Found {len(jobs)} jobs")
  print(jobs[0])
  ```

- [ ] 运行手动测试：`python test_manual.py`
- [ ] 验证返回数据格式正确

### 📝 补充单元测试

- [ ] 创建文件 `tests/test_indeed_adapter.py`
- [ ] 编写测试：`test_indeed_adapter_returns_jobs()`
- [ ] 编写测试：`test_indeed_adapter_platform_name()`
- [ ] 编写测试：`test_indeed_adapter_data_transformation()`
- [ ] 运行测试：`pytest tests/test_indeed_adapter.py`
- [ ] 确认通过

---

## Phase 2.3: 集成到 FastAPI

- [ ] 更新 `app/main.py` 的 `/scrape/indeed` 端点
  ```python
  from app.adapters.indeed_adapter import IndeedAdapter

  @app.post("/scrape/indeed")
  async def scrape_indeed(request: ScrapeRequest):
      adapter = IndeedAdapter()
      jobs = adapter.scrape(request)
      return ScrapeResponse(
          platform=PlatformEnum.INDEED,
          jobs=jobs,
          count=len(jobs)
      )
  ```

- [ ] 启动服务：`uvicorn app.main:app --reload`
- [ ] 访问 Swagger UI: http://localhost:8000/docs
- [ ] 测试 `/scrape/indeed` 端点
  ```json
  {
    "keywords": "tiler",
    "location": "Adelaide",
    "max_results": 10
  }
  ```
- [ ] 验证返回数据正确

- [ ] 更新 API 文档示例（在 Swagger 中查看）

---

## ✅ 最终检查清单

### 代码质量

- [ ] 所有测试通过：`pytest`
- [ ] 测试覆盖率 ≥ 80%：`pytest --cov=app tests/`
- [ ] 代码有类型注解
- [ ] 函数有文档字符串
- [ ] 没有明显的代码重复

### 功能验证

- [ ] `parse_location()` 正确解析各种地点格式
- [ ] `extract_trade()` 正确识别常见 Trade
- [ ] `normalize_employment_type()` 正确标准化工作类型
- [ ] `IndeedAdapter` 成功抓取 Indeed 数据
- [ ] API 端点返回正确的 JSON 格式

### 文档更新

- [ ] 代码注释清晰
- [ ] README.md 更新（如有必要）
- [ ] 测试文档说明（如有必要）

---

## 🎯 完成标准

**阶段 2 完成的标志：**

1. ✅ 所有工具函数通过 TDD 实现
2. ✅ Indeed 适配器成功抓取数据
3. ✅ 数据转换正确映射到 JobPostingDTO
4. ✅ API 端点正常工作
5. ✅ 测试覆盖率达标

**完成后应该能够：**
```bash
# 1. 所有测试通过
pytest

# 2. 启动服务
uvicorn app.main:app --reload

# 3. 成功调用 API
curl -X POST "http://localhost:8000/scrape/indeed" \
  -H "Content-Type: application/json" \
  -d '{"keywords": "tiler", "location": "Adelaide", "max_results": 10}'

# 4. 返回真实的职位数据
```

---

## 📚 参考资料

- [TDD_DEVELOPMENT_GUIDE.md](TDD_DEVELOPMENT_GUIDE.md) - TDD 方法论
- [SCRAPER_IMPLEMENTATION_PLAN.md](SCRAPER_IMPLEMENTATION_PLAN.md) - 总体计划
- [SCRAPER_DATA_FIELDS_ANALYSIS.md](SCRAPER_DATA_FIELDS_ANALYSIS.md) - 数据字段映射

---

**提示：** 完成一项就打勾 ✅，保持进度可视化！
