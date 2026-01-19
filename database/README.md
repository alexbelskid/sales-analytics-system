# Database

This directory contains database-related files for the Sales Analytics System.

## Structure

```
database/
├── schema/        # SQL table and view definitions
├── migrations/    # Database migration scripts  
├── seeds/         # Sample/test data for development
└── README.md      # This file
```

## Quick Start

### 1. Database Setup

The application uses **Supabase** (PostgreSQL) as the database.

**Connection details are in:**
- Backend: `backend/.env` → `SUPABASE_URL`, `SUPABASE_KEY`

### 2. Schema

Main tables:
- `sales` - Sales transactions
- `products` - Product catalog
- `customers` - Customer information
- `agents` - Sales agents
- `sale_items` - Line items (links sales ↔ products)

Analytics views:
- `product_performance` - Product statistics
- `agent_performance` - Agent KPIs
- `daily_sales_summary` - Daily aggregates
- `monthly_sales_trends` - Monthly trends

### 3. Seeds (Sample Data)

For local development, you can use:
- `seeds/sample_sales.csv` - Example sales data

**To populate database:**
```bash
# Run SQL scripts from main project docs
# See: docs/guides/database-setup.md
```

## Migrations

Database schema changes are managed through:
1. Supabase Dashboard SQL Editor (for production)
2. Migration scripts (for version control)

**Currently:** Manual migrations via Supabase UI

**Future:** Automated migration system

## Related Documentation

- [Database Setup Guide](../docs/guides/database-setup.md)
- [Supabase Setup](../docs/QUICKSTART.md#database-setup)
- [Troubleshooting](../docs/TROUBLESHOOTING.md#database-issues)
