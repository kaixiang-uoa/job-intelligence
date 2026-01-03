"""
测试 SeekAdapter 类

测试 SEEK 职位数据适配器的核心方法，包括：
- URL 参数构建
- 描述提取逻辑
- 职位数据转换
- 边缘情况处理
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from app.adapters.seek_adapter import SeekAdapter
from app.models.job_posting_dto import JobPostingDTO, ScrapeRequest, PlatformEnum


# ========================================
# 测试 _build_params() - URL 参数构建
# ========================================

def test_build_params_basic():
    """测试基本参数构建：keywords + results_wanted"""
    adapter = SeekAdapter()
    params = adapter._build_params("plumber", 10)

    assert params["siteKey"] == "AU-Main"
    assert params["keywords"] == "plumber"
    assert params["pageSize"] == 10
    assert params["page"] == 1
    assert params["locale"] == "en-AU"
    assert params["where"] == "All Australia"


def test_build_params_max_results():
    """测试最大结果数：50"""
    adapter = SeekAdapter()
    params = adapter._build_params("electrician", 50)

    assert params["pageSize"] == 50


def test_build_params_keywords_with_spaces():
    """测试带空格的关键词：junior plumber"""
    adapter = SeekAdapter()
    params = adapter._build_params("junior plumber", 20)

    assert params["keywords"] == "junior plumber"


# ========================================
# 测试 _extract_description() - 描述提取
# ========================================

def test_extract_description_from_teaser():
    """测试从 teaser 提取描述（优先级 1）"""
    adapter = SeekAdapter()
    job_data = {
        "teaser": "<p>Great opportunity for experienced plumber</p>",
        "bulletPoints": ["Point 1", "Point 2"]
    }

    description = adapter._extract_description(job_data)

    assert description == "Great opportunity for experienced plumber"
    assert "<p>" not in description  # HTML 已清理


def test_extract_description_from_bullet_points():
    """测试从 bulletPoints 提取描述（优先级 2）"""
    adapter = SeekAdapter()
    job_data = {
        "bulletPoints": ["Competitive salary", "Flexible hours", "Great team"]
    }

    description = adapter._extract_description(job_data)

    assert description == "Competitive salary • Flexible hours • Great team"


def test_extract_description_truncate_long_teaser():
    """测试长描述截断：限制 500 字符"""
    adapter = SeekAdapter()
    long_text = "A" * 600
    job_data = {
        "teaser": f"<p>{long_text}</p>"
    }

    description = adapter._extract_description(job_data)

    assert len(description) == 503  # 500 + "..."
    assert description.endswith("...")


def test_extract_description_truncate_long_bullet_points():
    """测试长 bulletPoints 截断"""
    adapter = SeekAdapter()
    job_data = {
        "bulletPoints": ["A" * 300, "B" * 300]
    }

    description = adapter._extract_description(job_data)

    assert len(description) == 503  # 500 + "..."
    assert description.endswith("...")


def test_extract_description_empty():
    """测试空描述：没有 teaser 和 bulletPoints"""
    adapter = SeekAdapter()
    job_data = {}

    description = adapter._extract_description(job_data)

    assert description is None


def test_extract_description_empty_teaser():
    """测试空 teaser（只有 HTML 标签）"""
    adapter = SeekAdapter()
    job_data = {
        "teaser": "<p></p>"
    }

    description = adapter._extract_description(job_data)

    # 空 HTML 清理后返回空字符串，应该返回 None
    assert description is None or description == ""


# ========================================
# 测试 _transform_job() - 数据转换
# ========================================

def test_transform_job_success():
    """测试正常职位转换：所有字段完整"""
    adapter = SeekAdapter()
    job_data = {
        "id": "12345",
        "title": "Plumber - Sydney",
        "advertiser": {
            "description": "ABC Plumbing"
        },
        "locations": [
            {"label": "Sydney, NSW"}  # 正确格式：suburb, state
        ],
        "teaser": "<p>Great opportunity for plumber</p>",
        "salaryLabel": "$70,000 - $80,000",
        "workTypes": ["Full time"],
        "listingDate": "2025-12-20T10:00:00Z"
    }

    job_dto = adapter._transform_job(job_data)

    assert job_dto is not None
    assert job_dto.source == PlatformEnum.SEEK
    assert job_dto.source_id == "12345"
    assert job_dto.title == "Plumber - Sydney"
    assert job_dto.company == "ABC Plumbing"
    assert job_dto.location_suburb == "Sydney"
    assert job_dto.location_state == "NSW"
    assert job_dto.trade == "plumber"  # extract_trade() 返回小写
    assert job_dto.employment_type == "Full Time"  # normalize_employment_type() 返回 "Full Time"
    assert job_dto.pay_range_min == 70000.0
    assert job_dto.pay_range_max == 80000.0
    assert "Great opportunity" in job_dto.description
    assert job_dto.job_url == "https://www.seek.com.au/job/12345"
    assert isinstance(job_dto.posted_at, datetime)


def test_transform_job_missing_id():
    """测试缺少必需字段：id - 应该抛出 ScraperValidationError"""
    from app.exceptions import ScraperValidationError

    adapter = SeekAdapter()
    job_data = {
        "title": "Plumber"
    }

    # 缺少必需字段，应该抛出验证错误
    with pytest.raises(ScraperValidationError) as exc_info:
        adapter._transform_job(job_data)

    assert "id" in str(exc_info.value)
    assert exc_info.value.field == "id"


def test_transform_job_missing_title():
    """测试缺少必需字段：title - 应该抛出 ScraperValidationError"""
    from app.exceptions import ScraperValidationError

    adapter = SeekAdapter()
    job_data = {
        "id": "12345"
    }

    # 缺少必需字段，应该抛出验证错误
    with pytest.raises(ScraperValidationError) as exc_info:
        adapter._transform_job(job_data)

    assert "title" in str(exc_info.value)
    assert exc_info.value.field == "title"


def test_transform_job_no_company():
    """测试缺少 company：使用默认值 'Unknown'"""
    adapter = SeekAdapter()
    job_data = {
        "id": "12345",
        "title": "Plumber",
        "advertiser": {}
    }

    job_dto = adapter._transform_job(job_data)

    assert job_dto is not None
    assert job_dto.company == "Unknown"


def test_transform_job_no_location():
    """测试缺少 location：suburb 和 state 为 None"""
    adapter = SeekAdapter()
    job_data = {
        "id": "12345",
        "title": "Plumber",
        "locations": []
    }

    job_dto = adapter._transform_job(job_data)

    assert job_dto is not None
    assert job_dto.location_suburb is None
    assert job_dto.location_state is None


def test_transform_job_invalid_salary():
    """测试无效薪资格式：parse_salary_range 返回 (None, None)"""
    adapter = SeekAdapter()
    job_data = {
        "id": "12345",
        "title": "Plumber",
        "salaryLabel": "Competitive"  # 无法解析的格式
    }

    job_dto = adapter._transform_job(job_data)

    assert job_dto is not None
    assert job_dto.pay_range_min is None
    assert job_dto.pay_range_max is None


def test_transform_job_no_work_type():
    """测试缺少 workTypes：employment_type 为 None"""
    adapter = SeekAdapter()
    job_data = {
        "id": "12345",
        "title": "Plumber",
        "workTypes": []
    }

    job_dto = adapter._transform_job(job_data)

    assert job_dto is not None
    assert job_dto.employment_type is None


def test_transform_job_invalid_date():
    """测试无效日期格式：posted_at 为 None"""
    adapter = SeekAdapter()
    job_data = {
        "id": "12345",
        "title": "Plumber",
        "listingDate": "invalid-date"
    }

    job_dto = adapter._transform_job(job_data)

    assert job_dto is not None
    assert job_dto.posted_at is None


def test_transform_job_alternative_company_field():
    """测试备选 company 字段：companyName"""
    adapter = SeekAdapter()
    job_data = {
        "id": "12345",
        "title": "Plumber",
        "advertiser": {},  # 没有 description
        "companyName": "XYZ Plumbing"
    }

    job_dto = adapter._transform_job(job_data)

    assert job_dto is not None
    assert job_dto.company == "XYZ Plumbing"


def test_transform_job_employer_name_fallback():
    """测试 employer.name 作为 company 的备选"""
    adapter = SeekAdapter()
    job_data = {
        "id": "12345",
        "title": "Plumber",
        "advertiser": {},
        "employer": {
            "name": "ABC Corp"
        }
    }

    job_dto = adapter._transform_job(job_data)

    assert job_dto is not None
    assert job_dto.company == "ABC Corp"


# ========================================
# 测试 scrape() - 集成测试（使用 mock）
# ========================================

@patch('app.adapters.seek_adapter.requests.get')
def test_scrape_success(mock_get):
    """测试成功抓取职位"""
    # Mock API 响应
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "id": "12345",
                "title": "Plumber",
                "advertiser": {"description": "ABC Plumbing"},
                "locations": [{"label": "Sydney, NSW"}],
                "teaser": "<p>Great job</p>",
                "salaryLabel": "$70,000 - $80,000",
                "workTypes": ["Full time"],
                "listingDate": "2025-12-20T10:00:00Z"
            }
        ],
        "totalCount": 1
    }
    mock_get.return_value = mock_response

    adapter = SeekAdapter()
    request = ScrapeRequest(keywords="plumber", location="All Australia")

    jobs = adapter.scrape(request)

    assert len(jobs) == 1
    assert jobs[0].title == "Plumber"
    assert jobs[0].company == "ABC Plumbing"


@patch('app.adapters.seek_adapter.requests.get')
def test_scrape_empty_results(mock_get):
    """测试空结果"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [],
        "totalCount": 0
    }
    mock_get.return_value = mock_response

    adapter = SeekAdapter()
    request = ScrapeRequest(keywords="nonexistent-job", location="All Australia")

    jobs = adapter.scrape(request)

    assert len(jobs) == 0


@patch('app.adapters.seek_adapter.requests.get')
def test_scrape_partial_failures(mock_get):
    """测试部分职位转换失败（缺少必需字段）"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {"id": "1", "title": "Plumber"},  # 有效
            {"id": "2"},  # 无效（缺少 title）
            {"title": "Electrician"},  # 无效（缺少 id）
            {"id": "3", "title": "Carpenter"}  # 有效
        ],
        "totalCount": 4
    }
    mock_get.return_value = mock_response

    adapter = SeekAdapter()
    request = ScrapeRequest(keywords="trade", location="All Australia")

    jobs = adapter.scrape(request)

    # 只有 2 个有效职位
    assert len(jobs) == 2
    assert jobs[0].source_id == "1"
    assert jobs[1].source_id == "3"


@patch('app.adapters.seek_adapter.requests.get')
def test_scrape_max_results_adjustment(mock_get):
    """测试 max_results 超出范围时自动调整为 50"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": [], "totalCount": 0}
    mock_get.return_value = mock_response

    adapter = SeekAdapter()
    request = ScrapeRequest(keywords="plumber", location="All Australia", max_results=100)  # 超出范围

    jobs = adapter.scrape(request)

    # 验证调用参数（pageSize 被调整为 50）
    call_args = mock_get.call_args
    assert call_args[1]['params']['pageSize'] == 50
