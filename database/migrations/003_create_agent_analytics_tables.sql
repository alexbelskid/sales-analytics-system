-- Migration: Create Agent Analytics Tables
-- Description: Creates tables for agent sales plans, daily sales tracking, and AI-powered forecasts
-- Date: 2026-01-09

-- ============================================================================
-- Table: agent_sales_plans
-- Description: Stores monthly sales plans for agents
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_sales_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    plan_amount DECIMAL(15, 2) NOT NULL CHECK (plan_amount >= 0),
    region VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_agent_plan_period UNIQUE(agent_id, period_start, period_end)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_sales_plans_agent ON agent_sales_plans(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_sales_plans_period ON agent_sales_plans(period_start, period_end);
CREATE INDEX IF NOT EXISTS idx_agent_sales_plans_region ON agent_sales_plans(region);

-- RLS policies
ALTER TABLE agent_sales_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public access to agent_sales_plans" ON agent_sales_plans
    FOR ALL USING (true) WITH CHECK (true);

-- ============================================================================
-- Table: agent_daily_sales
-- Description: Stores daily sales data for agents for historical analysis
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_daily_sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    sale_date DATE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount >= 0),
    region VARCHAR(100),
    category VARCHAR(100), -- БелПочта, Потребкооперация, ПИРОТЕХНИКА, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_agent_daily_sale UNIQUE(agent_id, sale_date, category)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_daily_sales_agent ON agent_daily_sales(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_daily_sales_date ON agent_daily_sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_agent_daily_sales_region ON agent_daily_sales(region);
CREATE INDEX IF NOT EXISTS idx_agent_daily_sales_category ON agent_daily_sales(category);

-- RLS policies
ALTER TABLE agent_daily_sales ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public access to agent_daily_sales" ON agent_daily_sales
    FOR ALL USING (true) WITH CHECK (true);

-- ============================================================================
-- Table: agent_performance_forecasts
-- Description: Stores AI-generated forecasts for agent performance
-- ============================================================================
CREATE TABLE IF NOT EXISTS agent_performance_forecasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    predicted_amount DECIMAL(15, 2) NOT NULL CHECK (predicted_amount >= 0),
    predicted_fulfillment_percent DECIMAL(5, 2) NOT NULL CHECK (predicted_fulfillment_percent >= 0),
    confidence_score DECIMAL(5, 2) CHECK (confidence_score >= 0 AND confidence_score <= 100),
    ai_insights JSONB, -- Structured AI analysis and recommendations
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_agent_forecast UNIQUE(agent_id, forecast_date, period_start)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_forecasts_agent ON agent_performance_forecasts(agent_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_date ON agent_performance_forecasts(forecast_date);
CREATE INDEX IF NOT EXISTS idx_forecasts_period ON agent_performance_forecasts(period_start, period_end);

-- RLS policies
ALTER TABLE agent_performance_forecasts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public access to agent_performance_forecasts" ON agent_performance_forecasts
    FOR ALL USING (true) WITH CHECK (true);

-- ============================================================================
-- Modify existing agents table
-- Description: Add fields for regional analytics and cached statistics
-- ============================================================================
ALTER TABLE agents ADD COLUMN IF NOT EXISTS region VARCHAR(100);
ALTER TABLE agents ADD COLUMN IF NOT EXISTS current_month_sales DECIMAL(15, 2) DEFAULT 0;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS current_month_plan DECIMAL(15, 2) DEFAULT 0;
ALTER TABLE agents ADD COLUMN IF NOT EXISTS total_lifetime_sales DECIMAL(15, 2) DEFAULT 0;

-- Index for region filtering
CREATE INDEX IF NOT EXISTS idx_agents_region ON agents(region);

-- ============================================================================
-- Update triggers for timestamp management
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_agent_sales_plans_updated_at
    BEFORE UPDATE ON agent_sales_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Helper functions for analytics
-- ============================================================================

-- Function to calculate agent performance for a period
CREATE OR REPLACE FUNCTION get_agent_performance(
    p_agent_id UUID,
    p_period_start DATE,
    p_period_end DATE
)
RETURNS TABLE (
    agent_id UUID,
    agent_name VARCHAR,
    region VARCHAR,
    plan_amount DECIMAL,
    actual_sales DECIMAL,
    fulfillment_percent DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        a.name,
        a.region,
        COALESCE(asp.plan_amount, 0) as plan_amount,
        COALESCE(SUM(ads.amount), 0) as actual_sales,
        CASE 
            WHEN COALESCE(asp.plan_amount, 0) > 0 
            THEN (COALESCE(SUM(ads.amount), 0) / asp.plan_amount * 100)
            ELSE 0
        END as fulfillment_percent
    FROM agents a
    LEFT JOIN agent_sales_plans asp ON a.id = asp.agent_id 
        AND asp.period_start = p_period_start 
        AND asp.period_end = p_period_end
    LEFT JOIN agent_daily_sales ads ON a.id = ads.agent_id 
        AND ads.sale_date BETWEEN p_period_start AND p_period_end
    WHERE a.id = p_agent_id
    GROUP BY a.id, a.name, a.region, asp.plan_amount;
END;
$$ LANGUAGE plpgsql;

-- Function to get regional performance summary
CREATE OR REPLACE FUNCTION get_regional_performance(
    p_region VARCHAR,
    p_period_start DATE,
    p_period_end DATE
)
RETURNS TABLE (
    region VARCHAR,
    total_plan DECIMAL,
    total_sales DECIMAL,
    fulfillment_percent DECIMAL,
    agents_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.region,
        COALESCE(SUM(asp.plan_amount), 0) as total_plan,
        COALESCE(SUM(ads_agg.daily_sales), 0) as total_sales,
        CASE 
            WHEN COALESCE(SUM(asp.plan_amount), 0) > 0 
            THEN (COALESCE(SUM(ads_agg.daily_sales), 0) / SUM(asp.plan_amount) * 100)
            ELSE 0
        END as fulfillment_percent,
        COUNT(DISTINCT a.id) as agents_count
    FROM agents a
    LEFT JOIN agent_sales_plans asp ON a.id = asp.agent_id 
        AND asp.period_start = p_period_start 
        AND asp.period_end = p_period_end
    LEFT JOIN (
        SELECT agent_id, SUM(amount) as daily_sales
        FROM agent_daily_sales
        WHERE sale_date BETWEEN p_period_start AND p_period_end
        GROUP BY agent_id
    ) ads_agg ON a.id = ads_agg.agent_id
    WHERE a.region = p_region AND a.is_active = true
    GROUP BY a.region;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Comments for documentation
-- ============================================================================
COMMENT ON TABLE agent_sales_plans IS 'Stores monthly sales plans assigned to agents';
COMMENT ON TABLE agent_daily_sales IS 'Tracks daily sales performance for each agent with category breakdown';
COMMENT ON TABLE agent_performance_forecasts IS 'AI-generated forecasts and insights for agent performance';
COMMENT ON COLUMN agents.region IS 'Geographic region assignment (БРЕСТ, ВИТЕБСК, ГОМЕЛЬ, ГРОДНО, МИНСК)';
COMMENT ON COLUMN agents.current_month_sales IS 'Cached current month sales for quick dashboard display';
COMMENT ON COLUMN agents.current_month_plan IS 'Cached current month plan for quick dashboard display';
