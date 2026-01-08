-- ============================================================================
-- Reload Supabase Schema Cache
-- Run this in Supabase SQL Editor to make PostgREST see new tables
-- ============================================================================

-- Notify PostgREST to reload schema cache
NOTIFY pgrst, 'reload schema';

-- Alternative: Grant permissions explicitly
GRANT ALL ON knowledge_base TO anon, authenticated, service_role;
GRANT ALL ON training_examples TO anon, authenticated, service_role;

-- Grant usage on sequences if any
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;

-- Verify table is accessible
SELECT 'knowledge_base accessible' as status, count(*) as rows FROM knowledge_base
UNION ALL
SELECT 'training_examples accessible' as status, count(*) as rows FROM training_examples;
