-- =================================================================
-- Reset Analytics Data Function
-- Efficiently clears large tables and ensures clean state
-- =================================================================

CREATE OR REPLACE FUNCTION reset_analytics_data()
RETURNS void AS $$
BEGIN
    -- 1. Truncate main data tables (Cascade to sale_items)
    TRUNCATE TABLE sales CASCADE;
    
    -- 2. Clear import history
    TRUNCATE TABLE import_history CASCADE;
    
    -- 3. Clear generated AI knowledge related to sales analytics
    -- Assuming 'sales_insight' or similar category for auto-generated insights
    DELETE FROM knowledge_base WHERE category IN ('sales_insight', 'auto_generated');
    
    -- Note: We generally preserve Customers and Products as they might be master data,
    -- but if they are purely from import, they might be stale. 
    -- For now, we keep them to avoid breaking other links, but Sales and Import History are wiped.
END;
$$ LANGUAGE plpgsql;

GRANT EXECUTE ON FUNCTION reset_analytics_data TO authenticated;
GRANT EXECUTE ON FUNCTION reset_analytics_data TO service_role;
