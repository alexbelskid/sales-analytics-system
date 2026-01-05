-- ============================================
-- MIGRATION: Add missing columns to existing tables
-- Run this in Supabase SQL Editor
-- ============================================

-- Add normalized_name to customers if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'customers' AND column_name = 'normalized_name'
    ) THEN
        ALTER TABLE customers ADD COLUMN normalized_name TEXT;
        UPDATE customers SET normalized_name = LOWER(TRIM(name));
        ALTER TABLE customers ALTER COLUMN normalized_name SET NOT NULL;
    END IF;
END $$;

-- Add missing columns to customers
ALTER TABLE customers ADD COLUMN IF NOT EXISTS total_purchases DECIMAL(15,2) DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS purchases_count INTEGER DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS last_purchase_date DATE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Add normalized_name to products if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'products' AND column_name = 'normalized_name'
    ) THEN
        ALTER TABLE products ADD COLUMN normalized_name TEXT;
        UPDATE products SET normalized_name = LOWER(TRIM(name));
        ALTER TABLE products ALTER COLUMN normalized_name SET NOT NULL;
    END IF;
END $$;

-- Add missing columns to products
ALTER TABLE products ADD COLUMN IF NOT EXISTS category TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS total_quantity DECIMAL(15,2) DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS total_revenue DECIMAL(15,2) DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS sales_count INTEGER DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- ============================================
-- Create stores table if not exists
-- ============================================
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT,
    name TEXT NOT NULL,
    region TEXT,
    channel TEXT,
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- Add missing columns to sales table
-- ============================================
ALTER TABLE sales ADD COLUMN IF NOT EXISTS store_id UUID REFERENCES stores(id);
ALTER TABLE sales ADD COLUMN IF NOT EXISTS year INTEGER;
ALTER TABLE sales ADD COLUMN IF NOT EXISTS month INTEGER;
ALTER TABLE sales ADD COLUMN IF NOT EXISTS week INTEGER;
ALTER TABLE sales ADD COLUMN IF NOT EXISTS day_of_week INTEGER;
ALTER TABLE sales ADD COLUMN IF NOT EXISTS price DECIMAL(15,2);

-- Update year/month/week for existing sales records
UPDATE sales SET 
    year = EXTRACT(YEAR FROM sale_date),
    month = EXTRACT(MONTH FROM sale_date),
    week = EXTRACT(WEEK FROM sale_date),
    day_of_week = EXTRACT(DOW FROM sale_date)
WHERE year IS NULL AND sale_date IS NOT NULL;

-- ============================================
-- Create import_history table
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
-- Create indexes
-- ============================================
CREATE INDEX IF NOT EXISTS idx_customers_normalized ON customers(normalized_name);
CREATE INDEX IF NOT EXISTS idx_customers_total ON customers(total_purchases DESC);
CREATE INDEX IF NOT EXISTS idx_products_normalized ON products(normalized_name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_revenue ON products(total_revenue DESC);
CREATE INDEX IF NOT EXISTS idx_stores_name ON stores(name);
CREATE INDEX IF NOT EXISTS idx_stores_region ON stores(region);
CREATE INDEX IF NOT EXISTS idx_sales_store ON sales(store_id);
CREATE INDEX IF NOT EXISTS idx_sales_year_month ON sales(year, month);
CREATE INDEX IF NOT EXISTS idx_sales_customer_date ON sales(customer_id, sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_product_date ON sales(product_id, sale_date);
CREATE INDEX IF NOT EXISTS idx_import_status ON import_history(status);

-- ============================================
-- DONE! Run this migration in Supabase SQL Editor
-- ============================================
SELECT 'Migration completed successfully!' as result;
