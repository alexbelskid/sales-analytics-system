DROP FUNCTION IF EXISTS get_top_customers_by_revenue(INT);
DROP FUNCTION IF EXISTS get_top_customers_by_revenue(INT, INT);
DROP FUNCTION IF EXISTS get_top_products_by_sales(INT);
DROP FUNCTION IF EXISTS get_top_products_by_sales(INT, INT);
DROP FUNCTION IF EXISTS get_sales_trend_monthly(INT);
DROP FUNCTION IF EXISTS get_dashboard_metrics(DATE, DATE, UUID);
DROP FUNCTION IF EXISTS reset_analytics_data();

DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS import_history CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS stores CASCADE;
DROP TABLE IF EXISTS knowledge_base CASCADE;

-- 1. TABLES
CREATE TABLE customers (
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

CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_customers_normalized ON customers(normalized_name);
CREATE INDEX idx_customers_total ON customers(total_purchases DESC);

CREATE TABLE products (
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

CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_products_normalized ON products(normalized_name);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_revenue ON products(total_revenue DESC);

CREATE TABLE stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT,
    name TEXT NOT NULL,
    region TEXT,
    channel TEXT,
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT stores_code_unique UNIQUE (code)
);

CREATE INDEX idx_stores_name ON stores(name);
CREATE INDEX idx_stores_region ON stores(region);

CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sale_date DATE NOT NULL,
    customer_id UUID REFERENCES customers(id),
    product_id UUID REFERENCES products(id),
    store_id UUID REFERENCES stores(id),
    quantity DECIMAL(15,4) NOT NULL DEFAULT 1,
    price DECIMAL(15,2),
    total_amount DECIMAL(15,2) NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    week INTEGER,
    day_of_week INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_sales_product ON sales(product_id);
CREATE INDEX idx_sales_store ON sales(store_id);
CREATE INDEX idx_sales_year_month ON sales(year, month);

CREATE TABLE import_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    file_size BIGINT,
    total_rows INTEGER,
    imported_rows INTEGER DEFAULT 0,
    failed_rows INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',
    progress_percent INTEGER DEFAULT 0,
    error_log TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_import_status ON import_history(status);
CREATE INDEX idx_import_uploaded ON import_history(uploaded_at DESC);

CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    category TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_knowledge_category ON knowledge_base(category);


-- 2. READ FUNCTIONS (ANALYTICS)

-- Dashboard Metrics
CREATE OR REPLACE FUNCTION get_dashboard_metrics(
    p_start_date DATE DEFAULT NULL,
    p_end_date DATE DEFAULT NULL,
    p_customer_id UUID DEFAULT NULL
)
RETURNS TABLE (
    total_revenue NUMERIC,
    total_sales BIGINT,
    average_check NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(SUM(total_amount), 0)::NUMERIC as total_revenue,
        COUNT(*)::BIGINT as total_sales,
        CASE WHEN COUNT(*) > 0 THEN COALESCE(SUM(total_amount), 0)::NUMERIC / COUNT(*) ELSE 0 END as average_check
    FROM sales
    WHERE (p_start_date IS NULL OR sale_date >= p_start_date)
      AND (p_end_date IS NULL OR sale_date <= p_end_date)
      AND (p_customer_id IS NULL OR customer_id = p_customer_id);
END;
$$ LANGUAGE plpgsql;

-- Top Customers (Updated signature to match Python)
CREATE OR REPLACE FUNCTION get_top_customers_by_revenue(
    p_limit INT DEFAULT 10,
    p_days INT DEFAULT 36500  -- Default 100 years to include everything
)
RETURNS TABLE (
    customer_id UUID,
    customer_name TEXT,
    total_revenue NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.name::TEXT,
        COALESCE(SUM(s.total_amount), 0)::NUMERIC as revenue
    FROM customers c
    LEFT JOIN sales s ON c.id = s.customer_id
    WHERE s.sale_date >= (CURRENT_DATE - (p_days || ' days')::INTERVAL)
    GROUP BY c.id, c.name
    ORDER BY revenue DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Top Products (Updated signature)
CREATE OR REPLACE FUNCTION get_top_products_by_sales(
    p_limit INT DEFAULT 10,
    p_days INT DEFAULT 36500
)
RETURNS TABLE (
    product_id UUID,
    product_name TEXT,
    total_quantity NUMERIC,
    total_revenue NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.name::TEXT,
        COALESCE(SUM(s.quantity), 0)::NUMERIC,
        COALESCE(SUM(s.total_amount), 0)::NUMERIC
    FROM products p
    LEFT JOIN sales s ON p.id = s.product_id
    WHERE s.sale_date >= (CURRENT_DATE - (p_days || ' days')::INTERVAL)
    GROUP BY p.id, p.name
    ORDER BY total_revenue DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Sales Trend (Missing function)
CREATE OR REPLACE FUNCTION get_sales_trend_monthly(p_months INT DEFAULT 120)
RETURNS TABLE (
    period TEXT,
    total_revenue NUMERIC,
    orders_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        TO_CHAR(sale_date, 'YYYY-MM') as period,
        COALESCE(SUM(total_amount), 0)::NUMERIC as total_revenue,
        COUNT(*)::BIGINT as orders_count
    FROM sales
    WHERE sale_date >= (CURRENT_DATE - (p_months || ' months')::INTERVAL)
    GROUP BY period
    ORDER BY period ASC;
END;
$$ LANGUAGE plpgsql;

-- Reset Data
CREATE OR REPLACE FUNCTION reset_analytics_data()
RETURNS JSON AS $$
DECLARE
    deleted_kb INT;
BEGIN
    TRUNCATE TABLE sales CASCADE;
    TRUNCATE TABLE import_history CASCADE;
    
    DELETE FROM knowledge_base 
    WHERE category IN ('sales_insight', 'auto_generated');
    
    GET DIAGNOSTICS deleted_kb = ROW_COUNT;
    
    RETURN json_build_object(
        'success', true,
        'deleted_sales', 'all',
        'deleted_imports', 'all',
        'deleted_knowledge', deleted_kb
    );
END;
$$ LANGUAGE plpgsql;
