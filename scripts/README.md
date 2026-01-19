# Scripts

Utility scripts for development, deployment, and maintenance.

## Structure

```
scripts/
├── dev/            # Development scripts
│   └── start_dev.sh
├── deploy/         # Deployment automation
└── maintenance/    # Database and system maintenance
    ├── insert_sales.py
    ├── setup_analytics.py
    └── update_coords.py
```

## Development Scripts

### `dev/start_dev.sh`

Starts both backend and frontend for local development.

```bash
./scripts/dev/start_dev.sh
```

**What it does:**
- Starts FastAPI backend on http://localhost:8000
- Starts Next.js frontend on http://localhost:3000

## Maintenance Scripts

### `maintenance/insert_sales.py`

Utility to insert sales data into Supabase.

```bash
cd scripts/maintenance
python insert_sales.py
```

### `maintenance/setup_analytics.py`

Sets up analytics views and aggregations.

```bash
python scripts/maintenance/setup_analytics.py
```

### `maintenance/update_coords.py`

Updates geographic coordinates for customers/stores.

```bash
python scripts/maintenance/update_coords.py
```

## Usage Tips

**Running scripts:**
```bash
# From project root
./scripts/dev/start_dev.sh

# Or navigate to script directory
cd scripts/maintenance
python insert_sales.py
```

**Environment:**
- Scripts use `.env` from backend directory
- Ensure `SUPABASE_URL` and `SUPABASE_KEY` are set

## Related Documentation

- [Quick Start](../docs/QUICKSTART.md)
- [Deployment Guide](../docs/DEPLOYMENT.md)
- [Troubleshooting](../docs/TROUBLESHOOTING.md)
