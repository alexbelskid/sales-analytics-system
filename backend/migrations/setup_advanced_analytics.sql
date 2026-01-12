-- Advanced Analytics Setup Migration
-- Run this in Supabase SQL Editor

-- =============================================
-- 1. ADD MISSING COLUMNS TO EXISTING TABLES
-- =============================================

-- Add region to customers if not exists
ALTER TABLE customers ADD COLUMN IF NOT EXISTS region TEXT;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS latitude DECIMAL(10, 7);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS longitude DECIMAL(10, 7);

-- Add category to products if not exists
ALTER TABLE products ADD COLUMN IF NOT EXISTS category TEXT;

-- Add agent_name to sales if not exists  
ALTER TABLE sales ADD COLUMN IF NOT EXISTS agent_name TEXT;

-- =============================================
-- 2. UPDATE EXISTING CUSTOMERS WITH REGIONS
-- =============================================

-- Assign random regions to customers without region
UPDATE customers 
SET region = (
    CASE floor(random() * 6)::int
        WHEN 0 THEN 'Минск'
        WHEN 1 THEN 'Брест'
        WHEN 2 THEN 'Гродно'
        WHEN 3 THEN 'Витебск'
        WHEN 4 THEN 'Могилёв'
        ELSE 'Гомель'
    END
),
latitude = (
    CASE floor(random() * 6)::int
        WHEN 0 THEN 53.9045
        WHEN 1 THEN 52.0976
        WHEN 2 THEN 53.6884
        WHEN 3 THEN 55.1904
        WHEN 4 THEN 53.9168
        ELSE 52.4345
    END
),
longitude = (
    CASE floor(random() * 6)::int
        WHEN 0 THEN 27.5615
        WHEN 1 THEN 23.6877
        WHEN 2 THEN 23.8258
        WHEN 3 THEN 30.2049
        WHEN 4 THEN 30.3449
        ELSE 30.9754
    END
)
WHERE region IS NULL;

-- =============================================
-- 3. UPDATE PRODUCTS WITH CATEGORIES
-- =============================================

UPDATE products 
SET category = (
    CASE floor(random() * 5)::int
        WHEN 0 THEN 'Электроника'
        WHEN 1 THEN 'Бытовая техника'
        WHEN 2 THEN 'Одежда'
        WHEN 3 THEN 'Продукты питания'
        ELSE 'Товары для дома'
    END
)
WHERE category IS NULL;

-- =============================================
-- 4. UPDATE SALES WITH AGENT NAMES
-- =============================================

UPDATE sales 
SET agent_name = (
    CASE floor(random() * 5)::int
        WHEN 0 THEN 'Иванов Александр'
        WHEN 1 THEN 'Петрова Мария'
        WHEN 2 THEN 'Сидоров Дмитрий'
        WHEN 3 THEN 'Козлова Анна'
        ELSE 'Новиков Сергей'
    END
)
WHERE agent_name IS NULL;

-- =============================================
-- 5. CREATE SALES_PLANS TABLE IF NOT EXISTS
-- =============================================

CREATE TABLE IF NOT EXISTS sales_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period DATE NOT NULL,
    product_id UUID REFERENCES products(id),
    customer_id UUID REFERENCES customers(id),
    agent_id UUID,
    planned_amount DECIMAL(15, 2) DEFAULT 0,
    planned_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- =============================================
-- 6. INSERT SAMPLE SALES PLANS
-- =============================================

-- Current month plan
INSERT INTO sales_plans (period, planned_amount, planned_quantity)
SELECT 
    DATE_TRUNC('month', CURRENT_DATE)::date,
    1500000,
    750
WHERE NOT EXISTS (
    SELECT 1 FROM sales_plans 
    WHERE period = DATE_TRUNC('month', CURRENT_DATE)::date
);

-- Previous month plan
INSERT INTO sales_plans (period, planned_amount, planned_quantity)
SELECT 
    (DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month')::date,
    1200000,
    600
WHERE NOT EXISTS (
    SELECT 1 FROM sales_plans 
    WHERE period = (DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month')::date
);

-- =============================================
-- 7. VERIFY SETUP
-- =============================================

-- Check customers have regions
SELECT 'Customers with regions: ' || COUNT(*)::text FROM customers WHERE region IS NOT NULL;

-- Check products have categories
SELECT 'Products with categories: ' || COUNT(*)::text FROM products WHERE category IS NOT NULL;

-- Check sales have agents
SELECT 'Sales with agents: ' || COUNT(*)::text FROM sales WHERE agent_name IS NOT NULL;

-- Check sales_plans
SELECT 'Sales plans: ' || COUNT(*)::text FROM sales_plans;
