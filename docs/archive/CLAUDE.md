# Sales Analytics System - Project Map

> **Context Brain**: This file provides comprehensive project context for AI assistants (Claude, etc.)

## 📋 Project Overview

**Sales Analytics System** — full-stack application for sales data analysis, automation, and AI-powered insights.

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Next.js 16 (React 18, TypeScript)
- **Database**: Supabase (PostgreSQL)
- **Deployment**: Railway
- **ML/AI**: Google Gemini, OpenAI, Prophet (forecasting)

---

## 🏗️ Architecture

```
new bi project/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py            # FastAPI entry point, CORS, routes
│   │   ├── config.py          # Environment configuration
│   │   ├── database.py        # Supabase client initialization
│   │   ├── models/            # Pydantic models (7 files)
│   │   ├── routers/           # API endpoints (20 routers)
│   │   │   ├── analytics.py
│   │   │   ├── agent_analytics.py
│   │   │   ├── advanced_analytics.py
│   │   │   ├── upload.py
│   │   │   ├── import_router.py
│   │   │   ├── inbox.py
│   │   │   ├── ai.py
│   │   │   ├── forecast.py
│   │   │   ├── salary.py
│   │   │   ├── proposals.py
│   │   │   └── ...
│   │   └── services/          # Business logic (16 services)
│   │       ├── analytics_service.py
│   │       ├── agent_analytics_service.py
│   │       ├── ai_service.py
│   │       ├── email_connector.py
│   │       ├── excel_parser.py
│   │       ├── forecast_service.py
│   │       ├── google_sheets_importer.py
│   │       ├── encryption_service.py
│   │       └── ...
│   ├── requirements.txt       # Python dependencies
│   └── tests/                 # Backend tests
│
├── frontend/                  # Next.js application
│   ├── src/
│   │   ├── app/              # App Router pages (13 routes)
│   │   │   ├── page.tsx      # Dashboard (/)
│   │   │   ├── analytics/
│   │   │   ├── agents/
│   │   │   ├── forecast/
│   │   │   ├── inbox/
│   │   │   ├── settings/
│   │   │   └── ...
│   │   ├── components/        # React components (42 components)
│   │   │   ├── ui/           # shadcn/ui components
│   │   │   ├── Sidebar.tsx
│   │   │   ├── MobileHeader.tsx
│   │   │   └── ...
│   │   ├── lib/
│   │   │   ├── utils.ts      # Utility functions
│   │   │   └── supabase.ts   # Supabase client
│   │   └── hooks/            # Custom React hooks
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── database/                  # Database schemas & migrations
│   └── migrations/
│
├── supabase/                  # Supabase configuration
│   └── migrations/
│
├── scripts/                   # Utility scripts
│
├── .env                       # Environment variables (gitignored)
├── .env.example               # Example env file
├── docker-compose.yml         # Local development setup
├── railway.json               # Railway deployment config
├── nixpacks.toml              # Nixpacks build config
└── start_dev.sh               # Development startup script
```

---

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: via Supabase (cloud or local)

### Environment Setup

1. **Copy environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Configure `.env`**:
   ```env
   # Supabase
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-key
   
   # AI Services
   GOOGLE_API_KEY=your-gemini-key
   OPENAI_API_KEY=your-openai-key
   
   # Frontend
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   ```

### Development Commands

#### Backend

```bash
# Navigate to project root
cd "/Users/alexbelski/Desktop/new bi project"

# Create virtual environment (if not exists)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run development server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend runs on**: `http://localhost:8000`  
**API docs**: `http://localhost:8000/docs`

#### Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

**Frontend runs on**: `http://localhost:3000`

#### Full Stack (Recommended)

```bash
# From project root
./start_dev.sh
```

This script starts both backend and frontend concurrently.

---

## 🧪 Testing

### Backend Tests

```bash
# From project root
cd backend
pytest

# With coverage
pytest --cov=app tests/

# Specific test file
pytest tests/test_analytics.py
```

### Advanced Analytics Test

```bash
# From project root
./test_advanced_analytics.sh
```

### Frontend Tests

```bash
cd frontend
npm run lint
npm run build  # Validates TypeScript and build
```

---

## 📦 Build & Deployment

### Backend Production Build

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend Production Build

```bash
cd frontend
npm run build
npm run start
```

### Railway Deployment

- **Config**: `railway.json`, `nixpacks.toml`
- **Auto-deploy**: Pushes to main branch trigger deployment
- **Environment**: Set all `.env` variables in Railway dashboard

---

## 🎨 Code Style & Conventions

### Python (Backend)

- **Style**: PEP 8
- **Formatter**: Black (line length: 100)
- **Type hints**: Required for function signatures
- **Imports**: Organized (stdlib → third-party → local)
- **Naming**:
  - `snake_case` for functions, variables, files
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

**Example**:
```python
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from app.models.sales import SalesData

router = APIRouter()

async def get_sales_data(
    start_date: str,
    end_date: str,
    agent_id: Optional[int] = None
) -> List[SalesData]:
    """Fetch sales data with optional agent filter."""
    try:
        # Implementation
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### TypeScript/React (Frontend)

- **Style**: Airbnb-inspired
- **Formatter**: Prettier (via Next.js)
- **Components**: Functional components with hooks
- **Naming**:
  - `PascalCase` for components, types, interfaces
  - `camelCase` for functions, variables
  - `kebab-case` for file names (except components)

**Example**:
```typescript
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';

interface SalesChartProps {
  startDate: string;
  endDate: string;
}

export function SalesChart({ startDate, endDate }: SalesChartProps) {
  const [data, setData] = useState<SalesData[]>([]);
  
  useEffect(() => {
    fetchSalesData();
  }, [startDate, endDate]);
  
  const fetchSalesData = async () => {
    // Implementation
  };
  
  return (
    <Card>
      {/* Chart rendering */}
    </Card>
  );
}
```

### Git Commit Messages

- **Format**: `<type>: <description>`
- **Types**: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
- **Example**: `feat: add ABC/XYZ analysis to advanced analytics`

---

## 🔑 Key Features & Modules

### 1. **Sales Analytics**
- **Routes**: `/api/analytics/*`, `/api/advanced-analytics/*`
- **Services**: `analytics_service.py`, `extended_analytics_service.py`
- **Features**: Sales trends, top products/customers, ABC/XYZ analysis

### 2. **Agent Analytics**
- **Routes**: `/api/agent-analytics/*`
- **Services**: `agent_analytics_service.py`
- **Features**: Agent performance, regional analysis, salary calculation

### 3. **AI Assistant**
- **Routes**: `/api/ai/*`, `/api/inbox/*`
- **Services**: `ai_service.py`, `email_connector.py`, `ai_context_service.py`
- **Features**: Email auto-reply, knowledge base, training examples

### 4. **Forecasting**
- **Routes**: `/api/forecast/*`
- **Services**: `forecast_service.py`
- **Features**: Prophet-based sales forecasting, trend analysis

### 5. **Data Import**
- **Routes**: `/api/upload/*`, `/api/import/*`
- **Services**: `excel_parser.py`, `google_sheets_importer.py`, `import_service.py`
- **Features**: Excel/CSV upload, Google Sheets integration

### 6. **Proposals & Documents**
- **Routes**: `/api/proposals/*`
- **Services**: `document_service.py`
- **Features**: Commercial proposal generation (DOCX, PDF)

---

## 🗄️ Database Schema

**Main Tables** (Supabase):
- `sales_data` — Sales transactions
- `agents` — Sales agents
- `customers` — Customer information
- `products` — Product catalog
- `email_settings` — Email configuration
- `knowledge_base` — AI knowledge entries
- `training_examples` — AI training data
- `response_tones` — AI response tone presets

**Key Relationships**:
- `sales_data.agent_id` → `agents.id`
- `sales_data.customer_id` → `customers.id`
- `sales_data.product_id` → `products.id`

---

## 🔒 Security

- **Rate Limiting**: `slowapi` (100 req/min per IP)
- **Encryption**: `cryptography` for sensitive data
- **CORS**: Configured in `main.py`
- **Environment Variables**: Never commit `.env` to git
- **API Keys**: Stored in environment, never hardcoded

---

## 🐛 Troubleshooting

See [`TROUBLESHOOTING.md`](file:///Users/alexbelski/Desktop/new%20bi%20project/TROUBLESHOOTING.md) for common issues.

**Quick Fixes**:
- **Backend won't start**: Check `.env` variables, activate venv
- **Frontend build fails**: `rm -rf node_modules .next && npm install`
- **Database errors**: Verify Supabase credentials, check migrations
- **Import errors**: Ensure Python path includes `backend/app`

---

## 📚 Additional Documentation

- [`QUICKSTART.md`](file:///Users/alexbelski/Desktop/new%20bi%20project/QUICKSTART.md) — Fast setup guide
- [`LAUNCH_CHECKLIST.md`](file:///Users/alexbelski/Desktop/new%20bi%20project/LAUNCH_CHECKLIST.md) — Pre-deployment checklist
- [`STORAGE_SETUP.md`](file:///Users/alexbelski/Desktop/new%20bi%20project/STORAGE_SETUP.md) — File storage configuration
- [`ABC_XYZ_VERIFICATION.md`](file:///Users/alexbelski/Desktop/new%20bi%20project/ABC_XYZ_VERIFICATION.md) — ABC/XYZ analysis validation

---

## 🤖 AI Assistant Notes

When working with this codebase:

1. **Always check environment**: Ensure `.env` is configured before running commands
2. **Use absolute paths**: Project root is `/Users/alexbelski/Desktop/new bi project`
3. **Backend changes**: Restart `uvicorn` to see changes (unless `--reload` is active)
4. **Frontend changes**: Hot reload is automatic with `npm run dev`
5. **Database changes**: Run migrations, clear cache if schema changes
6. **Dependencies**: Update `requirements.txt` (backend) or `package.json` (frontend) when adding libraries
7. **Testing**: Always run tests before committing major changes
8. **Code style**: Follow PEP 8 (Python) and Prettier (TypeScript)

---

**Last Updated**: 2026-01-12  
**Maintained by**: Бин & Джек (закрытая банда программистов 🖤)
