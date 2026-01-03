"""
调试 SEEK API 响应格式
"""

import requests
import json

url = "https://www.seek.com.au/api/jobsearch/v5/search"
params = {
    "siteKey": "AU-Main",
    "where": "All Australia",
    "keywords": "plumber",
    "page": 1,
    "pageSize": 1,
    "locale": "en-AU"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

response = requests.get(url, params=params, headers=headers)
data = response.json()

print("=" * 80)
print("SEEK API 响应示例（第一个职位）")
print("=" * 80)
print(json.dumps(data.get("data", [])[0], indent=2, ensure_ascii=False))
print("=" * 80)
