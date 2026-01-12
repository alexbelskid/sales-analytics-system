#!/bin/bash
# Test script for new advanced analytics endpoints

BASE_URL="https://sales-analytics-system-production.up.railway.app"

echo "🧪 Testing Advanced Analytics Endpoints"
echo "========================================"
echo ""

# Test 1: Filter Options
echo "1️⃣ Testing /api/analytics/filter-options"
curl -s "$BASE_URL/api/analytics/filter-options" | python3 -m json.tool | head -20
echo ""
echo "---"
echo ""

# Test 2: LFL Comparison (last month vs this month)
echo "2️⃣ Testing /api/analytics/lfl (LFL comparison)"
PERIOD1_START="2025-01-01"
PERIOD1_END="2025-01-15"
PERIOD2_START="2024-12-01"
PERIOD2_END="2024-12-15"

curl -s "$BASE_URL/api/analytics/lfl?period1_start=$PERIOD1_START&period1_end=$PERIOD1_END&period2_start=$PERIOD2_START&period2_end=$PERIOD2_END" | python3 -m json.tool
echo ""
echo "---"
echo ""

# Test 3: Dashboard with filters
echo "3️⃣ Testing /api/analytics/dashboard with region filter"
curl -s "$BASE_URL/api/analytics/dashboard?region=Минск" | python3 -m json.tool
echo ""
echo "---"
echo ""

# Test 4: Top products with category filter
echo "4️⃣ Testing /api/analytics/top-products with category filter"
curl -s "$BASE_URL/api/analytics/top-products?category=Конфеты&limit=5" | python3 -m json.tool
echo ""
echo "---"
echo ""

echo "✅ All tests completed!"
