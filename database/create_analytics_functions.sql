-- ============================================================================
-- Analytics RPC Functions
-- These functions provide optimized aggregations for the analytics endpoints
-- ============================================================================

-- Drop existing functions if they exist
DROP FUNCTION IF EXISTS get_top_products_by_sales(INT, INT);
DROP FUNCTION IF EXISTS get_top_customers_by_revenue(INT, INT);
DROP FUNCTION IF EXISTS get_sales_trend(TEXT);

-- ============================================================================
-- Function: get_top_products_by_sales
-- Returns top products by total revenue
-- Parameters:
--   p_limit: Maximum number of products to return
--   p_days: Number of days to look back (from current date)
-- ============================================================================
CREATE OR REPLACE FUNCTION get_top_products_by_sales(
    p_limit INT DEFAULT 10,
    p_days INT DEFAULT 90
)
RETURNS TABLE (
    product_id TEXT,
    product_name TEXT,
    total_revenue NUMERIC,
    orders_count BIGINT,
    total_quantity NUMERIC
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    cutoff_date DATE;
BEGIN
    cutoff_date := CURRENT_DATE - p_days;
    
    RETURN QUERY
    SELECT 
        s.product_id::TEXT,
        COALESCE(p.name, 'Неизвестный товар') AS product_name,
        COALESCE(SUM(s.total_amount), 0)::NUMERIC AS total_revenue,
        COUNT(DISTINCT s.id)::BIGINT AS orders_count,
        COALESCE(SUM(s.quantity), 0)::NUMERIC AS total_quantity
    FROM sales s
    LEFT JOIN products p ON s.product_id = p.id
    WHERE s.sale_date >= cutoff_date
    GROUP BY s.product_id, p.name
    ORDER BY total_revenue DESC
    LIMIT p_limit;
END;
$$;

-- ============================================================================
-- Function: get_top_customers_by_revenue
-- Returns top customers by total revenue
-- Parameters:
--   p_limit: Maximum number of customers to return
--   p_days: Number of days to look back (from current date)
-- ============================================================================
CREATE OR REPLACE FUNCTION get_top_customers_by_revenue(
    p_limit INT DEFAULT 10,
    p_days INT DEFAULT 90
)
RETURNS TABLE (
    customer_id TEXT,
    customer_name TEXT,
    total_revenue NUMERIC,
    orders_count BIGINT,
    avg_order_value NUMERIC
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    cutoff_date DATE;
BEGIN
    cutoff_date := CURRENT_DATE - p_days;
    
    RETURN QUERY
    SELECT 
        s.customer_id::TEXT,
        COALESCE(c.name, 'Неизвестный клиент') AS customer_name,
        COALESCE(SUM(s.total_amount), 0)::NUMERIC AS total_revenue,
        COUNT(DISTINCT s.id)::BIGINT AS orders_count,
        COALESCE(AVG(s.total_amount), 0)::NUMERIC AS avg_order_value
    FROM sales s
    LEFT JOIN customers c ON s.customer_id = c.id
    WHERE s.sale_date >= cutoff_date
    GROUP BY s.customer_id, c.name
    ORDER BY total_revenue DESC
    LIMIT p_limit;
END;
$$;

-- ============================================================================
-- Function: get_sales_trend
-- Returns sales aggregated by period (day, week, month)
-- Parameters:
--   p_period: Aggregation period ('day', 'week', 'month')
-- ============================================================================
CREATE OR REPLACE FUNCTION get_sales_trend(
    p_period TEXT DEFAULT 'month'
)
RETURNS TABLE (
    period_date DATE,
    total_revenue NUMERIC,
    orders_count BIGINT,
    avg_order_value NUMERIC
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    IF p_period = 'day' THEN
        RETURN QUERY
        SELECT 
            s.sale_date::DATE AS period_date,
            COALESCE(SUM(s.total_amount), 0)::NUMERIC AS total_revenue,
            COUNT(s.id)::BIGINT AS orders_count,
            COALESCE(AVG(s.total_amount), 0)::NUMERIC AS avg_order_value
        FROM sales s
        GROUP BY s.sale_date
        ORDER BY s.sale_date;
    
    ELSIF p_period = 'week' THEN
        RETURN QUERY
        SELECT 
            DATE_TRUNC('week', s.sale_date)::DATE AS period_date,
            COALESCE(SUM(s.total_amount), 0)::NUMERIC AS total_revenue,
            COUNT(s.id)::BIGINT AS orders_count,
            COALESCE(AVG(s.total_amount), 0)::NUMERIC AS avg_order_value
        FROM sales s
        GROUP BY DATE_TRUNC('week', s.sale_date)
        ORDER BY period_date;
    
    ELSE -- default to 'month'
        RETURN QUERY
        SELECT 
            DATE_TRUNC('month', s.sale_date)::DATE AS period_date,
            COALESCE(SUM(s.total_amount), 0)::NUMERIC AS total_revenue,
            COUNT(s.id)::BIGINT AS orders_count,
            COALESCE(AVG(s.total_amount), 0)::NUMERIC AS avg_order_value
        FROM sales s
        GROUP BY DATE_TRUNC('month', s.sale_date)
        ORDER BY period_date;
    END IF;
END;
$$;

-- ============================================================================
-- Grant permissions to all roles
-- ============================================================================
GRANT EXECUTE ON FUNCTION get_top_products_by_sales(INT, INT) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION get_top_customers_by_revenue(INT, INT) TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION get_sales_trend(TEXT) TO anon, authenticated, service_role;

-- ============================================================================
-- Refresh schema cache
-- ============================================================================
NOTIFY pgrst, 'reload schema';

-- ============================================================================
-- Verification queries (optional - comment out for production)
-- ============================================================================
-- Test the functions
-- SELECT * FROM get_top_products_by_sales(5, 90);
-- SELECT * FROM get_top_customers_by_revenue(5, 90);
-- SELECT * FROM get_sales_trend('month');
