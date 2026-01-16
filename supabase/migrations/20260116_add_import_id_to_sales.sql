-- Migration: Add import_id to sales table for CASCADE deletion
-- Date: 2026-01-16
-- Description: Adds import_id column to track which import created each sale

-- Step 1: Add import_id column (nullable to allow existing records)
ALTER TABLE sales 
ADD COLUMN import_id UUID NULL;

-- Step 2: Add foreign key constraint to import_history
ALTER TABLE sales
ADD CONSTRAINT fk_sales_import_id 
FOREIGN KEY (import_id) 
REFERENCES import_history(id) 
ON DELETE CASCADE;  -- ✅ When import is deleted, sales are auto-deleted

-- Step 3: Create index for performance
CREATE INDEX idx_sales_import_id ON sales(import_id);

-- Step 4: Add comment
COMMENT ON COLUMN sales.import_id IS 'ID of import_history record that created this sale';

-- Note: Existing sales will have import_id = NULL
-- Future imports will populate this field automatically
