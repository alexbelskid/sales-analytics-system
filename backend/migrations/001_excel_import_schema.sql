-- ============================================
-- EXCEL IMPORT & ANALYTICS SCHEMA
-- Run this in Supabase SQL Editor
-- ============================================

-- Drop existing tables if recreating (CAREFUL!)
-- DROP TABLE IF EXISTS sales CASCADE;
-- DROP TABLE IF EXISTS import_history CASCADE;
-- DROP TABLE IF EXISTS customers CASCADE;
-- DROP TABLE IF EXISTS products CASCADE;
-- DROP TABLE IF EXISTS stores CASCADE;

-- ============================================
-- TABLE: customers
-- ============================================
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    total_purchases DECIMAL(15,2) DEFAULT 0,
    purchases_count INTEGER DEFAULT 0,
    last_purchase_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT customers_name_unique UNIQUE (normalized_name)
);

CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);
CREATE INDEX IF NOT EXISTS idx_customers_normalized ON customers(normalized_name);
CREATE INDEX IF NOT EXISTS idx_customers_total ON customers(total_purchases DESC);

-- ============================================
-- TABLE: products
-- ============================================
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    category TEXT,
    total_quantity DECIMAL(15,2) DEFAULT 0,
    total_revenue DECIMAL(15,2) DEFAULT 0,
    sales_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT products_name_unique UNIQUE (normalized_name)
);

CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_normalized ON products(normalized_name);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_revenue ON products(total_revenue DESC);

-- ============================================
-- TABLE: stores
-- ============================================
CREATE TABLE IF NOT EXISTS stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT,
    name TEXT NOT NULL,
    region TEXT,
    channel TEXT,
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT stores_code_unique UNIQUE (code)
);

CREATE INDEX IF NOT EXISTS idx_stores_name ON stores(name);
CREATE INDEX IF NOT EXISTS idx_stores_region ON stores(region);

-- ============================================
-- TABLE: sales (main transaction table)
-- ============================================
CREATE TABLE IF NOT EXISTS sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sale_date DATE NOT NULL,
    customer_id UUID REFERENCES customers(id),
    product_id UUID REFERENCES products(id),
    store_id UUID REFERENCES stores(id),
    quantity DECIMAL(15,4) NOT NULL,
    price DECIMAL(15,2),
    amount DECIMAL(15,2) NOT NULL,
    -- Denormalized for fast queries
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    week INTEGER,
    day_of_week INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Primary indexes for analytics
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_store ON sales(store_id);
CREATE INDEX IF NOT EXISTS idx_sales_year_month ON sales(year, month);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sales_customer_date ON sales(customer_id, sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_product_date ON sales(product_id, sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_year_product ON sales(year, product_id);
CREATE INDEX IF NOT EXISTS idx_sales_year_customer ON sales(year, customer_id);

-- ============================================
-- TABLE: import_history
-- ============================================
CREATE TABLE IF NOT EXISTS import_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    file_size BIGINT,
    total_rows INTEGER DEFAULT 0,
    imported_rows INTEGER DEFAULT 0,
    failed_rows INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
    error_log TEXT,
    progress_percent INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_import_status ON import_history(status);
CREATE INDEX IF NOT EXISTS idx_import_started ON import_history(started_at DESC);

-- ============================================
-- UPDATE TRIGGER for updated_at
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_customers_updated_at ON customers;
CREATE TRIGGER update_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_products_updated_at ON products;
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- DONE! Tables: 5, Indexes: 18
-- ============================================
