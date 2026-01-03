-- Knowledge Base Table
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category VARCHAR(100) NOT NULL CHECK (category IN ('products', 'terms', 'contacts', 'faq', 'company_info')),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster category queries
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_created ON knowledge_base(created_at DESC);

-- Training Examples Table
CREATE TABLE IF NOT EXISTS training_examples (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    tone VARCHAR(50) DEFAULT 'professional',
    confidence_score FLOAT DEFAULT 1.0 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for faster tone queries and confidence sorting
CREATE INDEX IF NOT EXISTS idx_training_tone ON training_examples(tone);
CREATE INDEX IF NOT EXISTS idx_training_confidence ON training_examples(confidence_score DESC);

-- Sample data for knowledge_base
INSERT INTO knowledge_base (category, title, content) VALUES
('products', 'Шоколад молочный', 'Цена: 5.50 BYN/кг. Высокое качество, натуральные ингредиенты. Минимальный заказ: 50 кг.'),
('products', 'Вафли', 'Цена: 4.20 BYN/кг. Различные вкусы. Минимальный заказ: 30 кг.'),
('terms', 'Условия доставки', 'Бесплатная доставка при заказе от 2000 BYN. Доставка по Минску: 1-2 дня. По Беларуси: 3-5 дней.'),
('terms', 'Минимальный заказ', 'Минимальная сумма заказа: 1000 BYN. Для постоянных клиентов возможны индивидуальные условия.'),
('contacts', 'Контактная информация', 'Email: sales@company.by, Телефон: +375 29 123-45-67, Адрес: г. Минск, ул. Примерная, 1'),
('faq', 'Как оформить заказ?', 'Отправьте заявку на email или позвоните. Менеджер свяжется с вами в течение часа.'),
('company_info', 'О компании', 'Мы занимаемся оптовыми поставками кондитерских изделий с 2010 года. Работаем с крупнейшими производителями Беларуси.');

-- Sample data for training_examples
INSERT INTO training_examples (question, answer, tone, confidence_score) VALUES
('Какая цена на шоколад?', 'Здравствуйте! Цена на шоколад молочный составляет 5.50 BYN/кг. Минимальный заказ - 50 кг. Доставка бесплатная при заказе от 2000 BYN.', 'professional', 1.0),
('Какие условия доставки?', 'Добрый день! Доставка бесплатная при заказе от 2000 BYN. По Минску доставляем за 1-2 дня, по Беларуси - 3-5 дней.', 'professional', 1.0),
('Минимальный заказ?', 'Здравствуйте! Минимальная сумма заказа составляет 1000 BYN. Для постоянных клиентов возможны индивидуальные условия.', 'professional', 1.0);

-- Update trigger for knowledge_base
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_knowledge_updated_at BEFORE UPDATE ON knowledge_base
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
