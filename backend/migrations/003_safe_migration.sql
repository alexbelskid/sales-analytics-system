-- ============================================
-- MIGRATION: Add columns to existing schema
-- Adapted for your current sales table structure
-- ============================================

-- ============================================
-- 1. Add missing columns to SALES table
-- ============================================
ALTER TABLE sales ADD COLUMN IF NOT EXISTS store_id UUID;
ALTER TABLE sales ADD COLUMN IF NOT EXISTS year INTEGER;
ALTER TABLE sales ADD COLUMN IF NOT EXISTS month INTEGER;
ALTER TABLE sales ADD COLUMN IF NOT EXISTS week INTEGER;
ALTER TABLE sales ADD COLUMN IF NOT EXISTS day_of_week INTEGER;

-- Populate year/month/week from existing sale_date
UPDATE sales SET 
    year = EXTRACT(YEAR FROM sale_date)::INTEGER,
    month = EXTRACT(MONTH FROM sale_date)::INTEGER,
    week = EXTRACT(WEEK FROM sale_date)::INTEGER,
    day_of_week = EXTRACT(DOW FROM sale_date)::INTEGER
WHERE sale_date IS NOT NULL AND year IS NULL;

-- ============================================
-- 2. Add missing columns to CUSTOMERS table
-- ============================================
ALTER TABLE customers ADD COLUMN IF NOT EXISTS normalized_name TEXT;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS total_purchases DECIMAL(15,2) DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS purchases_count INTEGER DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS last_purchase_date DATE;

-- Populate normalized_name
UPDATE customers SET normalized_name = LOWER(TRIM(name)) WHERE normalized_name IS NULL;

-- ============================================
-- 3. Add missing columns to PRODUCTS table
-- ============================================
ALTER TABLE products ADD COLUMN IF NOT EXISTS normalized_name TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS category TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS total_quantity DECIMAL(15,2) DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS total_revenue DECIMAL(15,2) DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS sales_count INTEGER DEFAULT 0;

-- Populate normalized_name
UPDATE products SET normalized_name = LOWER(TRIM(name)) WHERE normalized_name IS NULL;

-- ============================================
-- 4. Create STORES table
-- ============================================
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE,
    name TEXT NOT NULL,
    region TEXT,
    channel TEXT,
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 5. Create IMPORT_HISTORY table
-- ============================================
CREATE TABLE IF NOT EXISTS import_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    file_size BIGINT,
    total_rows INTEGER DEFAULT 0,
    imported_rows INTEGER DEFAULT 0,
    failed_rows INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',
    error_log TEXT,
    progress_percent INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- ============================================
-- 6. Create indexes
-- ============================================
CREATE INDEX IF NOT EXISTS idx_sales_year_month ON sales(year, month);
CREATE INDEX IF NOT EXISTS idx_sales_store ON sales(store_id);
CREATE INDEX IF NOT EXISTS idx_customers_normalized ON customers(normalized_name);
CREATE INDEX IF NOT EXISTS idx_products_normalized ON products(normalized_name);
CREATE INDEX IF NOT EXISTS idx_stores_code ON stores(code);
CREATE INDEX IF NOT EXISTS idx_import_status ON import_history(status);

-- ============================================
-- 7. Add foreign key for store_id (optional, may fail if stores is empty)
-- ============================================
-- ALTER TABLE sales ADD CONSTRAINT fk_sales_store 
--     FOREIGN KEY (store_id) REFERENCES stores(id);

-- ============================================
-- DONE!
-- ============================================
SELECT 'Migration completed!' as result;
