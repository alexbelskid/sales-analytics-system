-- =================================================================
-- Fix Analytics RPC Functions: Type Mismatch and Missing Columns
-- =================================================================

-- 1. Drop existing functions to avoid conflicts
DROP FUNCTION IF EXISTS get_top_customers_by_revenue(int, int);
DROP FUNCTION IF EXISTS get_top_products_by_sales(int, int);

-- 2. Correct Top Customers Function (Handle VARCHAR/TEXT mismatch)
CREATE OR REPLACE FUNCTION get_top_customers_by_revenue(
    p_limit int DEFAULT 10,
    p_days int DEFAULT 365
)
RETURNS TABLE (
    customer_id uuid,
    customer_name text,
    total_revenue numeric,
    orders_count bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.customer_id,
        CAST(c.name AS text) as customer_name,  -- Explicit CAST to TEXT
        SUM(s.total_amount)::numeric as total_revenue,
        COUNT(*)::bigint as orders_count
    FROM sales s
    LEFT JOIN customers c ON c.id = s.customer_id
    WHERE s.sale_date >= CURRENT_DATE - p_days
    GROUP BY s.customer_id, c.name
    ORDER BY total_revenue DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- 3. Correct Top Products Function (Handle NULL product_id in sales)
CREATE OR REPLACE FUNCTION get_top_products_by_sales(
    p_limit int DEFAULT 10,
    p_days int DEFAULT 365
)
RETURNS TABLE (
    product_id uuid,
    product_name text,
    total_revenue numeric,
    orders_count bigint
) AS $$
DECLARE
    has_product_id boolean;
BEGIN
    -- Check if sales table has product_id column
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'sales' AND column_name = 'product_id'
    ) INTO has_product_id;
    
    IF has_product_id THEN
        RETURN QUERY
        SELECT 
            s.product_id,
            CAST(COALESCE(p.name, 'Неизвестный') AS text) as product_name,
            SUM(s.total_amount)::numeric as total_revenue,
            COUNT(*)::bigint as orders_count
        FROM sales s
        LEFT JOIN products p ON p.id = s.product_id
        WHERE s.sale_date >= CURRENT_DATE - p_days
        AND s.product_id IS NOT NULL -- Exclude NULL products
        GROUP BY s.product_id, p.name
        ORDER BY total_revenue DESC
        LIMIT p_limit;
    ELSE
        -- If no product_id (legacy), return products from products table with count 0
        RETURN QUERY
        SELECT 
            p.id as product_id,
            CAST(p.name AS text) as product_name,
            0::numeric as total_revenue,
            0::bigint as orders_count
        FROM products p
        LIMIT p_limit;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions again just in case
GRANT EXECUTE ON FUNCTION get_top_customers_by_revenue TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_top_products_by_sales TO anon, authenticated;
