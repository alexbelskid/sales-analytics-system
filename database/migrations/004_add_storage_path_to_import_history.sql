-- Migration: Add file storage support to import_history
-- Description: Adds storage_path field to track uploaded files in Supabase Storage
-- Date: 2026-01-11

-- Add storage_path column to import_history table
ALTER TABLE import_history 
ADD COLUMN IF NOT EXISTS storage_path TEXT;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_import_history_storage_path 
ON import_history(storage_path) 
WHERE storage_path IS NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN import_history.storage_path IS 'Path to the uploaded file in Supabase Storage bucket (import-files)';
