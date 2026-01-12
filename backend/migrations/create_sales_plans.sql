-- Plan-Fact Analysis: Sales Plans/Budgets Table
-- This table stores planned/budgeted sales targets for comparison with actual results

CREATE TABLE IF NOT EXISTS sales_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    period_type VARCHAR(20) DEFAULT 'month', -- 'day', 'week', 'month', 'quarter', 'year'
    
    -- Dimensions (optional filters)
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    agent_id UUID,
    region VARCHAR(100),
    category VARCHAR(100),
    
    -- Planned metrics
    planned_revenue DECIMAL(15, 2) NOT NULL DEFAULT 0,
    planned_quantity INTEGER DEFAULT 0,
    planned_orders INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),
    notes TEXT,
    
    -- Constraints
    CONSTRAINT valid_period CHECK (period_end >= period_start),
    CONSTRAINT positive_revenue CHECK (planned_revenue >= 0),
    CONSTRAINT positive_quantity CHECK (planned_quantity >= 0)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sales_plans_period ON sales_plans(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_sales_plans_product ON sales_plans(product_id) WHERE product_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sales_plans_customer ON sales_plans(customer_id) WHERE customer_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sales_plans_agent ON sales_plans(agent_id) WHERE agent_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_sales_plans_region ON sales_plans(region) WHERE region IS NOT NULL;

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_sales_plans_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sales_plans_updated_at
    BEFORE UPDATE ON sales_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_sales_plans_updated_at();

-- Sample data for testing (optional)
-- INSERT INTO sales_plans (period_start, period_end, period_type, planned_revenue, planned_quantity, planned_orders)
-- VALUES 
--     ('2025-01-01', '2025-01-31', 'month', 1000000, 5000, 200),
--     ('2025-02-01', '2025-02-28', 'month', 1200000, 6000, 250);
