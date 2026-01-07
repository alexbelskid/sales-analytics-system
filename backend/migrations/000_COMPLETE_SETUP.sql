DROP FUNCTION IF EXISTS get_top_customers_by_revenue(INT);
DROP FUNCTION IF EXISTS get_top_products_by_sales(INT);
DROP FUNCTION IF EXISTS reset_analytics_data();

DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS import_history CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS stores CASCADE;
DROP TABLE IF EXISTS knowledge_base CASCADE;

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
CREATE INDEX idx_sales_customer_date ON sales(customer_id, sale_date);
CREATE INDEX idx_sales_product_date ON sales(product_id, sale_date);

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

CREATE OR REPLACE FUNCTION get_top_customers_by_revenue(limit_count INT DEFAULT 10)
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
    GROUP BY c.id, c.name
    ORDER BY revenue DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_top_products_by_sales(limit_count INT DEFAULT 10)
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
    GROUP BY p.id, p.name
    ORDER BY total_revenue DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

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
