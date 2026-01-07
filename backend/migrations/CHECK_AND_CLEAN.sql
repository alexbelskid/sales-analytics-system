-- ============================================
-- SCRIPT TO CHECK AND CLEAN DUPLICATE DATA
-- ============================================

-- 1. CHECK CURRENT DATA
SELECT 
    'sales' as table_name,
    COUNT(*) as total_rows,
    SUM(total_amount) as total_amount,
    MIN(created_at) as first_import,
    MAX(created_at) as last_import
FROM sales
UNION ALL
SELECT 
    'customers',
    COUNT(*),
    NULL,
    MIN(created_at),
    MAX(created_at)
FROM customers
UNION ALL
SELECT 
    'products',
    COUNT(*),
    NULL,
    MIN(created_at),
    MAX(created_at)
FROM products;

-- 2. CHECK FOR DUPLICATES
SELECT 
    sale_date,
    customer_id,
    product_id,
    total_amount,
    COUNT(*) as duplicate_count
FROM sales
GROUP BY sale_date, customer_id, product_id, total_amount
HAVING COUNT(*) > 1
LIMIT 10;

-- 3. TO CLEAN ALL DATA (RUN THIS IF NEEDED):
-- SELECT reset_analytics_data();
