-- ============================================================================
-- AI Assistant Tables Migration
-- Run this in Supabase SQL Editor to create knowledge_base and training_examples tables
-- ============================================================================

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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

-- Update trigger for knowledge_base
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_knowledge_updated_at ON knowledge_base;
CREATE TRIGGER update_knowledge_updated_at BEFORE UPDATE ON knowledge_base
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- RLS Policies for knowledge_base
-- ============================================================================

ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all for authenticated and service role" ON knowledge_base;
CREATE POLICY "Allow all for authenticated and service role" 
ON knowledge_base
FOR ALL
USING (
  (SELECT auth.role()) IN ('authenticated', 'service_role', 'anon')
);

-- ============================================================================
-- RLS Policies for training_examples
-- ============================================================================

ALTER TABLE training_examples ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow all for authenticated and service role" ON training_examples;
CREATE POLICY "Allow all for authenticated and service role" 
ON training_examples
FOR ALL
USING (
  (SELECT auth.role()) IN ('authenticated', 'service_role', 'anon')
);

-- ============================================================================
-- Verify tables created
-- ============================================================================
SELECT 'knowledge_base' as table_name, count(*) as rows FROM knowledge_base
UNION ALL
SELECT 'training_examples' as table_name, count(*) as rows FROM training_examples;
