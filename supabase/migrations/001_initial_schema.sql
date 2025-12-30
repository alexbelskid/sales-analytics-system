-- =====================================================
-- Система аналитики продаж - Начальная схема БД
-- =====================================================

-- Клиенты
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    company VARCHAR(255),
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Товары/Продукты
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE,
    price DECIMAL(12,2) NOT NULL DEFAULT 0,
    cost_price DECIMAL(12,2) DEFAULT 0,
    category VARCHAR(100),
    description TEXT,
    unit VARCHAR(50) DEFAULT 'шт',
    in_stock INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Агенты (менеджеры по продажам)
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    base_salary DECIMAL(12,2) DEFAULT 0,
    commission_rate DECIMAL(5,2) DEFAULT 5.0,
    bonus_threshold DECIMAL(12,2) DEFAULT 100000,
    bonus_amount DECIMAL(12,2) DEFAULT 5000,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Продажи (основная таблица)
CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    sale_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
    discount DECIMAL(12,2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'completed',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Позиции продаж (товары в продаже)
CREATE TABLE sale_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sale_id UUID REFERENCES sales(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(12,2) NOT NULL,
    discount DECIMAL(12,2) DEFAULT 0,
    amount DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- База знаний для AI (RAG)
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(100) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT[],
    embedding vector(1536),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Прайс-листы
CREATE TABLE price_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Цены в прайс-листе
CREATE TABLE price_list_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    price_list_id UUID REFERENCES price_lists(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    price DECIMAL(12,2) NOT NULL,
    min_quantity INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Расчёты зарплат
CREATE TABLE salary_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    base_salary DECIMAL(12,2) NOT NULL,
    sales_amount DECIMAL(12,2) NOT NULL,
    commission DECIMAL(12,2) NOT NULL,
    bonus DECIMAL(12,2) DEFAULT 0,
    penalty DECIMAL(12,2) DEFAULT 0,
    total_salary DECIMAL(12,2) NOT NULL,
    notes TEXT,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(agent_id, year, month)
);

-- =====================================================
-- Индексы для оптимизации
-- =====================================================

CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_sales_agent ON sales(agent_id);
CREATE INDEX idx_sales_status ON sales(status);
CREATE INDEX idx_sale_items_sale ON sale_items(sale_id);
CREATE INDEX idx_sale_items_product ON sale_items(product_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_knowledge_category ON knowledge_base(category);
CREATE INDEX idx_salary_agent_period ON salary_calculations(agent_id, year, month);

-- =====================================================
-- Функции для агрегации (вызываются через RPC)
-- =====================================================

-- Топ клиентов по сумме продаж
CREATE OR REPLACE FUNCTION get_top_customers(limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    customer_id UUID,
    name VARCHAR,
    total DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.name, COALESCE(SUM(s.total_amount), 0) as total
    FROM customers c
    LEFT JOIN sales s ON s.customer_id = c.id
    GROUP BY c.id, c.name
    ORDER BY total DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Топ товаров по продажам
CREATE OR REPLACE FUNCTION get_top_products(limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    product_id UUID,
    name VARCHAR,
    total_quantity BIGINT,
    total_amount DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, COALESCE(SUM(si.quantity), 0)::BIGINT as total_quantity, 
           COALESCE(SUM(si.amount), 0) as total_amount
    FROM products p
    LEFT JOIN sale_items si ON si.product_id = p.id
    GROUP BY p.id, p.name
    ORDER BY total_amount DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Динамика продаж по периодам
CREATE OR REPLACE FUNCTION get_sales_trend(period_type VARCHAR DEFAULT 'month')
RETURNS TABLE (
    period TEXT,
    amount DECIMAL,
    count BIGINT
) AS $$
BEGIN
    IF period_type = 'day' THEN
        RETURN QUERY
        SELECT TO_CHAR(sale_date, 'YYYY-MM-DD') as period,
               SUM(total_amount) as amount,
               COUNT(*) as count
        FROM sales
        WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY TO_CHAR(sale_date, 'YYYY-MM-DD')
        ORDER BY period;
    ELSIF period_type = 'week' THEN
        RETURN QUERY
        SELECT TO_CHAR(DATE_TRUNC('week', sale_date), 'YYYY-WW') as period,
               SUM(total_amount) as amount,
               COUNT(*) as count
        FROM sales
        WHERE sale_date >= CURRENT_DATE - INTERVAL '12 weeks'
        GROUP BY DATE_TRUNC('week', sale_date)
        ORDER BY period;
    ELSE
        RETURN QUERY
        SELECT TO_CHAR(sale_date, 'YYYY-MM') as period,
               SUM(total_amount) as amount,
               COUNT(*) as count
        FROM sales
        WHERE sale_date >= CURRENT_DATE - INTERVAL '12 months'
        GROUP BY TO_CHAR(sale_date, 'YYYY-MM')
        ORDER BY period;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- RLS Политики (Row Level Security)
-- =====================================================

ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE sale_items ENABLE ROW LEVEL SECURITY;

-- Политики для authenticated пользователей (полный доступ)
CREATE POLICY "Allow all for authenticated" ON customers FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow all for authenticated" ON products FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow all for authenticated" ON agents FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow all for authenticated" ON sales FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Allow all for authenticated" ON sale_items FOR ALL USING (auth.role() = 'authenticated');

-- Политики для service_role (backend)
CREATE POLICY "Allow all for service" ON customers FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow all for service" ON products FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow all for service" ON agents FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow all for service" ON sales FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Allow all for service" ON sale_items FOR ALL USING (auth.role() = 'service_role');
