-- Fix RLS Performance Issues
-- This script optimizes RLS policies by wrapping auth functions in SELECT
-- and consolidating duplicate policies

-- ============================================================================
-- CONSOLIDATE POLICIES - Remove duplicate "Allow all for service" policies
-- and update "Allow all for authenticated" to cover all cases
-- ============================================================================

-- Agents table
DROP POLICY IF EXISTS "Allow all for service" ON public.agents;

-- Update authenticated policy to use optimized auth check
DROP POLICY IF EXISTS "Allow all for authenticated" ON public.agents;
CREATE POLICY "Allow all for authenticated users and service role" 
ON public.agents
FOR ALL
USING (
  (SELECT auth.role()) IN ('authenticated', 'service_role')
);

-- Sale Items table
DROP POLICY IF EXISTS "Allow all for service" ON public.sale_items;

DROP POLICY IF EXISTS "Allow all for authenticated" ON public.sale_items;
CREATE POLICY "Allow all for authenticated users and service role" 
ON public.sale_items
FOR ALL
USING (
  (SELECT auth.role()) IN ('authenticated', 'service_role')
);

-- ============================================================================
-- EMAIL SETTINGS - Consolidate policies
-- ============================================================================

DROP POLICY IF EXISTS "Service role full access on email_settings" ON public.email_settings;
DROP POLICY IF EXISTS "Authenticated access on email_settings" ON public.email_settings;

CREATE POLICY "Full access for authenticated and service role" 
ON public.email_settings
FOR ALL
USING (
  (SELECT auth.role()) IN ('authenticated', 'service_role')
);

-- ============================================================================
-- INCOMING EMAILS - Consolidate policies
-- ============================================================================

DROP POLICY IF EXISTS "Service role full access on incoming_emails" ON public.incoming_emails;
DROP POLICY IF EXISTS "Authenticated access on incoming_emails" ON public.incoming_emails;

CREATE POLICY "Full access for authenticated and service role" 
ON public.incoming_emails
FOR ALL
USING (
  (SELECT auth.role()) IN ('authenticated', 'service_role')
);

-- ============================================================================
-- EMAIL RESPONSES - Consolidate policies
-- ============================================================================

DROP POLICY IF EXISTS "Service role full access on email_responses" ON public.email_responses;
DROP POLICY IF EXISTS "Authenticated access on email_responses" ON public.email_responses;

CREATE POLICY "Full access for authenticated and service role" 
ON public.email_responses
FOR ALL
USING (
  (SELECT auth.role()) IN ('authenticated', 'service_role')
);

-- ============================================================================
-- RESPONSE TONE SETTINGS - Consolidate policies
-- ============================================================================

DROP POLICY IF EXISTS "Service role full access on response_tone_settings" ON public.response_tone_settings;
DROP POLICY IF EXISTS "Authenticated access on response_tone_settings" ON public.response_tone_settings;

CREATE POLICY "Full access for authenticated and service role" 
ON public.response_tone_settings
FOR ALL
USING (
  (SELECT auth.role()) IN ('authenticated', 'service_role')
);

-- ============================================================================
-- RESPONSE TEMPLATES - Consolidate policies
-- ============================================================================

DROP POLICY IF EXISTS "Service role full access on response_templates" ON public.response_templates;
DROP POLICY IF EXISTS "Authenticated access on response_templates" ON public.response_templates;

CREATE POLICY "Full access for authenticated and service role" 
ON public.response_templates
FOR ALL
USING (
  (SELECT auth.role()) IN ('authenticated', 'service_role')
);

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Run this to verify the changes:
-- SELECT schemaname, tablename, policyname 
-- FROM pg_policies 
-- WHERE schemaname = 'public' 
-- ORDER BY tablename, policyname;
