-- Migration: Email System
-- Tables: incoming_emails, email_responses, email_settings, response_tone_settings, response_templates

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Table: email_settings (connection configuration)
-- ============================================
CREATE TABLE IF NOT EXISTS email_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    email_address VARCHAR(255) NOT NULL,
    email_provider VARCHAR(100) NOT NULL, -- 'gmail', 'outlook', 'yandex', 'mail_ru', 'rambler', 'yahoo', 'custom'
    connection_type VARCHAR(50) NOT NULL DEFAULT 'imap', -- 'imap', 'gmail_api', 'graph_api'
    
    -- IMAP/SMTP settings
    imap_server VARCHAR(255),
    imap_port INTEGER DEFAULT 993,
    smtp_server VARCHAR(255),
    smtp_port INTEGER DEFAULT 587,
    use_ssl BOOLEAN DEFAULT true,
    
    -- Credentials (encrypted)
    password_encrypted TEXT,
    oauth_token_encrypted TEXT,
    oauth_refresh_token TEXT,
    
    -- Sync settings
    auto_sync_enabled BOOLEAN DEFAULT true,
    sync_interval_minutes INTEGER DEFAULT 10,
    last_sync_at TIMESTAMP,
    last_sync_error TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    connection_status VARCHAR(50) DEFAULT 'not_tested', -- 'not_tested', 'connected', 'error'
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- Table: incoming_emails
-- ============================================
CREATE TABLE IF NOT EXISTS incoming_emails (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    settings_id UUID REFERENCES email_settings(id) ON DELETE CASCADE,
    
    -- Email data
    message_id VARCHAR(255) UNIQUE, -- RFC Message-ID for deduplication
    sender_email VARCHAR(255) NOT NULL,
    sender_name VARCHAR(255),
    recipient_email VARCHAR(255),
    subject TEXT,
    body_text TEXT,
    body_html TEXT,
    
    -- Metadata
    received_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) DEFAULT 'new', -- 'new', 'read', 'draft_ready', 'replied', 'archived'
    category VARCHAR(100) DEFAULT 'other', -- 'sales', 'support', 'partnership', 'spam', 'other'
    priority VARCHAR(50) DEFAULT 'normal', -- 'urgent', 'high', 'normal', 'low'
    is_read BOOLEAN DEFAULT false,
    
    -- Threading
    in_reply_to VARCHAR(255),
    thread_id VARCHAR(255),
    
    -- Internal
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- Table: email_responses (drafts and sent replies)
-- ============================================
CREATE TABLE IF NOT EXISTS email_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email_id UUID REFERENCES incoming_emails(id) ON DELETE CASCADE,
    
    -- Response content
    draft_text TEXT,
    final_text TEXT,
    
    -- Tone used
    tone_id UUID,
    tone_name VARCHAR(100),
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'sending', 'sent', 'failed'
    sent_at TIMESTAMP WITH TIME ZONE,
    send_error TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- Table: response_tone_settings
-- ============================================
CREATE TABLE IF NOT EXISTS response_tone_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    
    -- Tone identity
    tone_name VARCHAR(100) NOT NULL, -- 'professional', 'friendly', 'formal', 'brief', 'sales', 'custom'
    display_name VARCHAR(255),
    description TEXT,
    is_default BOOLEAN DEFAULT false,
    is_system BOOLEAN DEFAULT false, -- true for built-in presets
    
    -- Tone characteristics (1-10 scale)
    formality_level INTEGER DEFAULT 5 CHECK (formality_level >= 1 AND formality_level <= 10),
    friendliness_level INTEGER DEFAULT 5 CHECK (friendliness_level >= 1 AND friendliness_level <= 10),
    detail_level INTEGER DEFAULT 5 CHECK (detail_level >= 1 AND detail_level <= 10),
    
    -- Style settings
    use_emojis BOOLEAN DEFAULT false,
    greeting_style VARCHAR(100) DEFAULT 'formal', -- 'formal', 'friendly', 'brief', 'none'
    greeting_text VARCHAR(255),
    closing_style VARCHAR(100) DEFAULT 'formal', -- 'formal', 'friendly', 'brief', 'none'
    closing_text VARCHAR(255),
    
    -- Language settings
    language VARCHAR(10) DEFAULT 'ru',
    use_you_formal BOOLEAN DEFAULT true, -- Вы vs ты
    
    -- Signature
    signature_text TEXT,
    
    -- Custom AI instructions
    custom_instructions TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- Table: response_templates
-- ============================================
CREATE TABLE IF NOT EXISTS response_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    
    -- Template info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) DEFAULT 'general', -- 'thanks', 'pricing', 'meeting', 'followup', 'general'
    
    -- Content
    template_text TEXT NOT NULL,
    placeholders JSONB DEFAULT '{}', -- {"client_name": "", "product_name": "", etc}
    
    -- Settings
    tone_id UUID REFERENCES response_tone_settings(id),
    language VARCHAR(10) DEFAULT 'ru',
    
    -- Stats
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- Indexes
-- ============================================
CREATE INDEX IF NOT EXISTS idx_incoming_emails_settings ON incoming_emails(settings_id);
CREATE INDEX IF NOT EXISTS idx_incoming_emails_status ON incoming_emails(status);
CREATE INDEX IF NOT EXISTS idx_incoming_emails_category ON incoming_emails(category);
CREATE INDEX IF NOT EXISTS idx_incoming_emails_received ON incoming_emails(received_at DESC);
CREATE INDEX IF NOT EXISTS idx_incoming_emails_sender ON incoming_emails(sender_email);
CREATE INDEX IF NOT EXISTS idx_incoming_emails_message_id ON incoming_emails(message_id);

CREATE INDEX IF NOT EXISTS idx_email_responses_email ON email_responses(email_id);
CREATE INDEX IF NOT EXISTS idx_email_responses_status ON email_responses(status);

CREATE INDEX IF NOT EXISTS idx_tone_settings_user ON response_tone_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_tone_settings_default ON response_tone_settings(is_default) WHERE is_default = true;

CREATE INDEX IF NOT EXISTS idx_templates_category ON response_templates(category);
CREATE INDEX IF NOT EXISTS idx_templates_user ON response_templates(user_id);

-- ============================================
-- Insert default tone presets
-- ============================================
INSERT INTO response_tone_settings (
    tone_name, display_name, description, is_system,
    formality_level, friendliness_level, detail_level,
    use_emojis, greeting_style, greeting_text, closing_style, closing_text,
    use_you_formal
) VALUES 
(
    'professional', 'Профессиональный', 'Деловой, но не холодный тон', true,
    8, 5, 7,
    false, 'formal', 'Здравствуйте', 'formal', 'С уважением',
    true
),
(
    'friendly', 'Дружелюбный', 'Тёплый и открытый тон', true,
    5, 9, 6,
    true, 'friendly', 'Добрый день', 'friendly', 'Всего доброго',
    true
),
(
    'formal', 'Официальный', 'Максимально формальный тон', true,
    10, 3, 9,
    false, 'formal', 'Уважаемый(ая)', 'formal', 'С уважением',
    true
),
(
    'brief', 'Краткий', 'Короткие, по существу ответы', true,
    6, 6, 3,
    false, 'brief', 'Здравствуйте', 'brief', 'Спасибо',
    true
),
(
    'sales', 'Продажи', 'Убедительный, ориентированный на решение', true,
    7, 8, 8,
    false, 'friendly', 'Добрый день', 'friendly', 'Буду рад помочь',
    true
)
ON CONFLICT DO NOTHING;

-- ============================================
-- Insert default templates
-- ============================================
INSERT INTO response_templates (
    name, description, category, template_text, placeholders
) VALUES 
(
    'Благодарность за обращение',
    'Стандартный ответ на первое письмо клиента',
    'thanks',
    'Здравствуйте, {client_name}!

Благодарим за ваше обращение. Мы получили ваш запрос и приступаем к его обработке.

Ответим вам в ближайшее время.

С уважением,
{sender_name}',
    '{"client_name": "Имя клиента", "sender_name": "Ваше имя"}'
),
(
    'Информация о ценах',
    'Ответ на запрос стоимости',
    'pricing',
    'Добрый день, {client_name}!

Спасибо за интерес к нашим продуктам/услугам.

По вашему запросу:
- {product_name}: {price}
- Срок поставки: {delivery_time}
- Условия оплаты: {payment_terms}

Готовы ответить на дополнительные вопросы.

С уважением,
{sender_name}',
    '{"client_name": "Имя клиента", "product_name": "Название товара", "price": "Цена", "delivery_time": "Срок", "payment_terms": "Условия", "sender_name": "Ваше имя"}'
),
(
    'Запрос на встречу',
    'Приглашение на встречу или звонок',
    'meeting',
    'Здравствуйте, {client_name}!

Будем рады встретиться для обсуждения.

Предлагаем следующие варианты:
- {date_option_1}
- {date_option_2}

Удобно ли вам какое-то из этих времён?

С уважением,
{sender_name}',
    '{"client_name": "Имя клиента", "date_option_1": "Дата и время 1", "date_option_2": "Дата и время 2", "sender_name": "Ваше имя"}'
),
(
    'Повторное письмо',
    'Напоминание при отсутствии ответа',
    'followup',
    'Добрый день, {client_name}!

Напоминаем о нашем предложении от {previous_date}.

Если у вас остались вопросы — будем рады ответить.

С уважением,
{sender_name}',
    '{"client_name": "Имя клиента", "previous_date": "Дата предыдущего письма", "sender_name": "Ваше имя"}'
)
ON CONFLICT DO NOTHING;

-- ============================================
-- RLS Policies (basic - enable for all authenticated)
-- ============================================
ALTER TABLE email_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE incoming_emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE response_tone_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE response_templates ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "Service role full access on email_settings" ON email_settings
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on incoming_emails" ON incoming_emails
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on email_responses" ON email_responses
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on response_tone_settings" ON response_tone_settings
    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Service role full access on response_templates" ON response_templates
    FOR ALL USING (auth.role() = 'service_role');

-- Allow authenticated users access (in real app, filter by user_id)
CREATE POLICY "Authenticated access on email_settings" ON email_settings
    FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated access on incoming_emails" ON incoming_emails
    FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated access on email_responses" ON email_responses
    FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated access on response_tone_settings" ON response_tone_settings
    FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated access on response_templates" ON response_templates
    FOR ALL USING (auth.role() = 'authenticated');
