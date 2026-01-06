-- Analytics RPC Functions for efficient aggregation
-- Run this in Supabase SQL Editor

-- 1. Dashboard Metrics Function
CREATE OR REPLACE FUNCTION get_dashboard_metrics(
    p_start_date date DEFAULT NULL,
    p_end_date date DEFAULT NULL,
    p_customer_id uuid DEFAULT NULL
)
RETURNS TABLE (
    total_revenue numeric,
    total_sales bigint,
    average_check numeric
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(SUM(total_amount), 0)::numeric as total_revenue,
        COUNT(*)::bigint as total_sales,
        CASE 
            WHEN COUNT(*) > 0 THEN ROUND(SUM(total_amount) / COUNT(*), 2)
            ELSE 0
        END::numeric as average_check
    FROM sales
    WHERE 
        (p_start_date IS NULL OR sale_date >= p_start_date)
        AND (p_end_date IS NULL OR sale_date <= p_end_date)
        AND (p_customer_id IS NULL OR customer_id = p_customer_id);
END;
$$ LANGUAGE plpgsql;


-- 2. Top Customers Function
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
        c.name as customer_name,
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


-- 3. Top Products Function
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
            COALESCE(p.name, 'Неизвестный') as product_name,
            SUM(s.total_amount)::numeric as total_revenue,
            COUNT(*)::bigint as orders_count
        FROM sales s
        LEFT JOIN products p ON p.id = s.product_id
        WHERE s.sale_date >= CURRENT_DATE - p_days
        GROUP BY s.product_id, p.name
        ORDER BY total_revenue DESC
        LIMIT p_limit;
    ELSE
        -- If no product_id, return products from products table with count 0
        RETURN QUERY
        SELECT 
            p.id as product_id,
            p.name as product_name,
            0::numeric as total_revenue,
            0::bigint as orders_count
        FROM products p
        LIMIT p_limit;
    END IF;
END;
$$ LANGUAGE plpgsql;


-- 4. Sales Trend Function (by month)
CREATE OR REPLACE FUNCTION get_sales_trend_monthly(
    p_months int DEFAULT 12
)
RETURNS TABLE (
    period text,
    total_revenue numeric,
    orders_count bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        TO_CHAR(sale_date, 'YYYY-MM') as period,
        SUM(total_amount)::numeric as total_revenue,
        COUNT(*)::bigint as orders_count
    FROM sales
    WHERE sale_date >= CURRENT_DATE - (p_months || ' months')::interval
    GROUP BY TO_CHAR(sale_date, 'YYYY-MM')
    ORDER BY period;
END;
$$ LANGUAGE plpgsql;


-- 5. Quick count function
CREATE OR REPLACE FUNCTION get_sales_count()
RETURNS bigint AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM sales);
END;
$$ LANGUAGE plpgsql;


-- Grant permissions
GRANT EXECUTE ON FUNCTION get_dashboard_metrics TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_top_customers_by_revenue TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_top_products_by_sales TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_sales_trend_monthly TO anon, authenticated;
GRANT EXECUTE ON FUNCTION get_sales_count TO anon, authenticated;
