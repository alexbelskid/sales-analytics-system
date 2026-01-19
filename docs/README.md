# Documentation Index

Welcome to the Sales Analytics System documentation!

## Quick Links

- [Quick Start Guide](./QUICKSTART.md) - Get up and running in 5 minutes
- [Deployment Guide](./DEPLOYMENT.md) - Deploy to production
- [Troubleshooting](./TROUBLESHOOTING.md) - Common issues and solutions

## Guides

Detailed how-to guides for specific tasks:

- [AI Setup Guide](./guides/ai-setup.md) - Configure the AI assistant
- [Database Setup](./guides/database-setup.md) - Set up Supabase and storage

## Architecture

Technical documentation:

- **Frontend:** Next.js + React + TypeScript + Tailwind CSS
- **Backend:** FastAPI + Python
- **Database:** Supabase (PostgreSQL)
- **AI:** GROQ (LLaMA 3.3 70B) for SQL generation and synthesis
- **Deployment:** Railway

## Examples

Configuration templates:

- [Environment Variables](./examples/.env.example) - Example .env file

## Archive

Historical documents (for reference only):

- [Phase 2 Completion](./archive/PHASE2_COMPLETE.md)
- [Launch Checklist](./archive/LAUNCH_CHECKLIST.md)
- And more...

---

## Project Structure

```
sales-analytics-system/
├── backend/          # FastAPI Python backend
├── frontend/         # Next.js React frontend  
├── database/         # Database schemas and seeds
├── docs/             # Documentation (you are here!)
├── scripts/          # Utility scripts
└── tests/            # Integration and E2E tests
```

For more details, see the main [README](../README.md).
