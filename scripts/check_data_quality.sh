#!/bin/bash

# ========================================
# MVP 数据质量快速检查脚本
# ========================================
# 用途：快速验证系统中的数据质量
# 使用：./check_data_quality.sh
# ========================================

set -e

echo "========================================"
echo "📊 Job Intelligence MVP - 数据质量检查"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 配置
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="jobintel"
DB_USER="admin"
DB_PASS="dev123"
API_URL="http://localhost:5000"

# ========================================
# 1. 检查服务状态
# ========================================
echo "1️⃣ 检查服务状态..."
echo "----------------------------------------"

# 检查数据库
if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL 数据库连接正常${NC}"
else
    echo -e "${RED}❌ PostgreSQL 数据库连接失败${NC}"
    exit 1
fi

# 检查 API
if curl -s "$API_URL/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ .NET API 运行正常${NC}"
else
    echo -e "${YELLOW}⚠️  .NET API 未运行（可能不影响数据检查）${NC}"
fi

echo ""

# ========================================
# 2. 数据库基础统计
# ========================================
echo "2️⃣ 数据库基础统计..."
echo "----------------------------------------"

psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << 'EOF'
-- 总职位数
SELECT '总职位数:', COUNT(*) FROM job_postings;

-- 活跃职位数
SELECT '活跃职位数:', COUNT(*) FROM job_postings WHERE is_active = true;

-- 最新职位发布时间
SELECT '最新职位时间:', MAX(posted_at) FROM job_postings;

-- 最早职位发布时间
SELECT '最早职位时间:', MIN(posted_at) FROM job_postings;
EOF

echo ""

# ========================================
# 3. 数据来源分布
# ========================================
echo "3️⃣ 数据来源分布..."
echo "----------------------------------------"

psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << 'EOF'
SELECT
    source AS "来源",
    COUNT(*) AS "职位数",
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM job_postings), 2) AS "占比%"
FROM job_postings
GROUP BY source
ORDER BY COUNT(*) DESC;
EOF

echo ""

# ========================================
# 4. 按 Trade 分布（Top 10）
# ========================================
echo "4️⃣ Trade 分布（Top 10）..."
echo "----------------------------------------"

psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << 'EOF'
SELECT
    COALESCE(trade, 'NULL') AS "Trade",
    COUNT(*) AS "职位数"
FROM job_postings
GROUP BY trade
ORDER BY COUNT(*) DESC
LIMIT 10;
EOF

echo ""

# ========================================
# 5. 按州分布
# ========================================
echo "5️⃣ 地点分布（按州）..."
echo "----------------------------------------"

psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << 'EOF'
SELECT
    COALESCE(location_state, 'NULL') AS "州",
    COUNT(*) AS "职位数",
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM job_postings), 2) AS "占比%"
FROM job_postings
GROUP BY location_state
ORDER BY COUNT(*) DESC;
EOF

echo ""

# ========================================
# 6. 数据质量检查
# ========================================
echo "6️⃣ 数据质量检查..."
echo "----------------------------------------"

psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << 'EOF'
-- 重复检查（相同 source_id）
WITH duplicates AS (
    SELECT source_id, COUNT(*) as count
    FROM job_postings
    GROUP BY source_id
    HAVING COUNT(*) > 1
)
SELECT
    CASE
        WHEN COUNT(*) = 0 THEN '✅ 无重复数据'
        ELSE '❌ 发现 ' || COUNT(*) || ' 个重复的 source_id'
    END AS "去重检查"
FROM duplicates;

-- Trade 提取成功率
SELECT
    '总职位数: ' || COUNT(*) AS "Trade 提取",
    'trade IS NOT NULL: ' || COUNT(trade) AS "提取成功",
    ROUND(100.0 * COUNT(trade) / COUNT(*), 2) || '%' AS "成功率"
FROM job_postings;

-- Location 提取成功率
SELECT
    '总职位数: ' || COUNT(*) AS "地点提取",
    'state IS NOT NULL: ' || COUNT(location_state) AS "提取成功",
    ROUND(100.0 * COUNT(location_state) / COUNT(*), 2) || '%' AS "成功率"
FROM job_postings;

-- 薪资数据完整性
SELECT
    '总职位数: ' || COUNT(*) AS "薪资数据",
    'pay_range_min IS NOT NULL: ' || COUNT(pay_range_min) AS "有薪资",
    ROUND(100.0 * COUNT(pay_range_min) / COUNT(*), 2) || '%' AS "完整性"
FROM job_postings;
EOF

echo ""

# ========================================
# 7. 采集任务统计
# ========================================
echo "7️⃣ 采集任务统计..."
echo "----------------------------------------"

psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << 'EOF'
SELECT
    source AS "来源",
    COUNT(*) AS "任务次数",
    SUM(jobs_fetched) AS "总抓取数",
    SUM(jobs_saved) AS "总保存数",
    MAX(started_at) AS "最后执行时间"
FROM ingest_runs
GROUP BY source
ORDER BY source;
EOF

echo ""

# ========================================
# 8. 最近 10 条职位预览
# ========================================
echo "8️⃣ 最近 10 条职位预览..."
echo "----------------------------------------"

psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << 'EOF'
SELECT
    id AS "ID",
    LEFT(title, 30) AS "标题",
    LEFT(company, 20) AS "公司",
    location_state AS "州",
    trade AS "Trade",
    TO_CHAR(posted_at, 'YYYY-MM-DD') AS "发布日期"
FROM job_postings
ORDER BY posted_at DESC
LIMIT 10;
EOF

echo ""

# ========================================
# 9. 数据质量评分
# ========================================
echo "9️⃣ 数据质量评分..."
echo "----------------------------------------"

QUALITY_SCORE=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -A << 'EOF'
WITH metrics AS (
    SELECT
        -- 去重得分（无重复 = 100分）
        CASE
            WHEN COUNT(DISTINCT source_id) = COUNT(*) THEN 100
            ELSE ROUND(100.0 * COUNT(DISTINCT source_id) / COUNT(*), 2)
        END AS dedup_score,

        -- Trade 提取得分
        ROUND(100.0 * COUNT(trade) / COUNT(*), 2) AS trade_score,

        -- Location 提取得分
        ROUND(100.0 * COUNT(location_state) / COUNT(*), 2) AS location_score
    FROM job_postings
)
SELECT ROUND((dedup_score + trade_score + location_score) / 3, 2)
FROM metrics;
EOF
)

echo "整体数据质量评分: $QUALITY_SCORE / 100"

if (( $(echo "$QUALITY_SCORE >= 95" | bc -l) )); then
    echo -e "${GREEN}✅ 优秀！数据质量达到生产标准${NC}"
elif (( $(echo "$QUALITY_SCORE >= 80" | bc -l) )); then
    echo -e "${YELLOW}⚠️  良好，但仍有优化空间${NC}"
else
    echo -e "${RED}❌ 数据质量需要改进${NC}"
fi

echo ""
echo "========================================"
echo "✅ 检查完成"
echo "========================================"
