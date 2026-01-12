-- Migration 007: Unified Import Tracking
-- Adds support for tracking all import types (Excel, CSV, Google Sheets)
-- and enables cascade deletion of related data

-- Add new columns to import_history table
ALTER TABLE import_history 
ADD COLUMN IF NOT EXISTS import_source VARCHAR(50) DEFAULT 'excel_upload',
ADD COLUMN IF NOT EXISTS import_type VARCHAR(50) DEFAULT 'sales',
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}',
ADD COLUMN IF NOT EXISTS related_agent_ids UUID[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS related_sale_ids UUID[] DEFAULT '{}';

-- Add storage_path if it doesn't exist (from previous migration)
ALTER TABLE import_history
ADD COLUMN IF NOT EXISTS storage_path TEXT;

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_import_source ON import_history(import_source);
CREATE INDEX IF NOT EXISTS idx_import_type ON import_history(import_type);
CREATE INDEX IF NOT EXISTS idx_related_agents ON import_history USING GIN(related_agent_ids);
CREATE INDEX IF NOT EXISTS idx_storage_path ON import_history(storage_path);

-- Add comments for documentation
COMMENT ON COLUMN import_history.import_source IS 'Source of import: excel_upload, google_sheets, csv_upload, manual';
COMMENT ON COLUMN import_history.import_type IS 'Type of data: sales, agents, customers, products';
COMMENT ON COLUMN import_history.metadata IS 'Additional metadata: period_start, period_end, sheet_url, regions, etc.';
COMMENT ON COLUMN import_history.related_agent_ids IS 'Array of agent IDs created/updated by this import';
COMMENT ON COLUMN import_history.related_sale_ids IS 'Array of sale IDs created by this import (for cascade deletion)';
COMMENT ON COLUMN import_history.storage_path IS 'Path to the uploaded file in Supabase Storage bucket';

-- Update existing records to have default values
UPDATE import_history 
SET import_source = 'excel_upload',
    import_type = 'sales',
    metadata = '{}'::jsonb
WHERE import_source IS NULL OR import_type IS NULL;
