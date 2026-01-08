-- ============================================================================
-- FIX: Drop and Recreate AI Tables
-- This forces PostgREST to reload the schema cache
-- ============================================================================

-- Step 1: Backup existing data (if any)
-- CREATE TABLE IF NOT EXISTS knowledge_base_backup AS SELECT * FROM knowledge_base;
-- CREATE TABLE IF NOT EXISTS training_examples_backup AS SELECT * FROM training_examples;

-- Step 2: Drop existing tables
DROP TABLE IF EXISTS knowledge_base CASCADE;
DROP TABLE IF EXISTS training_examples CASCADE;

-- Step 3: Recreate Knowledge Base Table
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(100) NOT NULL CHECK (category IN ('products', 'terms', 'contacts', 'faq', 'company_info')),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_knowledge_category ON knowledge_base(category);
CREATE INDEX idx_knowledge_created ON knowledge_base(created_at DESC);

-- Step 4: Recreate Training Examples Table
CREATE TABLE training_examples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    tone VARCHAR(50) DEFAULT 'professional',
    confidence_score FLOAT DEFAULT 1.0 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_training_tone ON training_examples(tone);
CREATE INDEX idx_training_confidence ON training_examples(confidence_score DESC);

-- Step 5: Enable RLS
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_examples ENABLE ROW LEVEL SECURITY;

-- Step 6: Create RLS policies (allow all for authenticated and anon)
CREATE POLICY "Allow all operations on knowledge_base" ON knowledge_base
    FOR ALL USING (true) WITH CHECK (true);

CREATE POLICY "Allow all operations on training_examples" ON training_examples  
    FOR ALL USING (true) WITH CHECK (true);

-- Step 7: Grant permissions
GRANT ALL ON knowledge_base TO anon, authenticated, service_role;
GRANT ALL ON training_examples TO anon, authenticated, service_role;

-- Step 8: Force schema cache reload
NOTIFY pgrst, 'reload schema';

-- Step 9: Insert sample data
INSERT INTO knowledge_base (category, title, content) VALUES
('products', 'Шоколад молочный', 'Цена: 5.50 BYN/кг. Высокое качество, натуральные ингредиенты. Минимальный заказ: 50 кг.'),
('products', 'Вафли', 'Цена: 4.20 BYN/кг. Различные вкусы. Минимальный заказ: 30 кг.'),
('terms', 'Условия доставки', 'Бесплатная доставка при заказе от 2000 BYN. Доставка по Минску: 1-2 дня. По Беларуси: 3-5 дней.'),
('contacts', 'Контактная информация', 'Email: sales@company.by, Телефон: +375 29 123-45-67'),
('faq', 'Как оформить заказ?', 'Отправьте заявку на email или позвоните. Менеджер свяжется с вами в течение часа.');

INSERT INTO training_examples (question, answer, tone, confidence_score) VALUES
('Какая цена на шоколад?', 'Здравствуйте! Цена на шоколад молочный составляет 5.50 BYN/кг. Минимальный заказ - 50 кг.', 'professional', 1.0),
('Какие условия доставки?', 'Добрый день! Доставка бесплатная при заказе от 2000 BYN. По Минску: 1-2 дня, по Беларуси: 3-5 дней.', 'professional', 1.0);

-- Step 10: Verify creation
SELECT 'knowledge_base' as table_name, count(*) as rows FROM knowledge_base
UNION ALL
SELECT 'training_examples', count(*) FROM training_examples;
