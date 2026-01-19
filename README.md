# Sales Analytics System

A comprehensive sales analytics platform for Belarus-based businesses, featuring an AI-powered assistant that provides intelligent insights from your sales data.

## 🚀 Quick Start

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd sales-analytics-system
```

2. **Set up environment**
```bash
# Copy environment template
cp docs/examples/.env.example backend/.env
cp docs/examples/.env.example frontend/.env.local

# Edit with your credentials
nano backend/.env  # Add SUPABASE_URL, GROQ_API_KEY, etc.
```

3. **Start development servers**
```bash
./scripts/dev/start_dev.sh
```

Visit:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

📖 **Full setup guide:** [docs/QUICKSTART.md](./docs/QUICKSTART.md)

---

## 📁 Project Structure

```
sales-analytics-system/
├── backend/              # 🐍 FastAPI Python backend
│   ├── app/             # Application code
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # Business logic (AI, SQL, etc.)
│   │   ├── models/      # Data models
│   │   └── utils/       # Utilities
│   └── tests/           # Backend unit tests
│
├── frontend/            # ⚛️ Next.js React frontend
│   ├── src/
│   │   ├── app/         # Next.js app router
│   │   ├── components/  # React components
│   │   └── lib/         # Utilities
│   └── public/          # Static assets
│
├── database/            # 💾 Database files
│   ├── schema/          # SQL schemas
│   ├── migrations/      # DB migrations
│   └── seeds/           # Sample data
│
├── docs/                # 📚 Documentation
│   ├── guides/          # How-to guides
│   ├── architecture/    # Technical docs
│   └── examples/        # Config templates
│
├── scripts/             # 🔧 Utility scripts
│   ├── dev/             # Development
│   ├── deploy/          # Deployment
│   └── maintenance/     # DB maintenance
│
└── tests/               # 🧪 Integration & E2E tests
    ├── integration/     # API tests
    ├── e2e/             # Browser tests
    └── fixtures/        # Test data
```

---

## 🎯 Features

### AI Assistant
- **Natural language queries** - Ask questions in Russian/English
- **SQL generation** - Automatically generates database queries
- **Real-time analysis** - Analyzes 22,000+ sales records
- **Business context** - Combines data with market knowledge
- **Visible reasoning** - Shows thinking process

### Analytics Dashboard
- **Sales overview** - Key metrics at a glance
- **Product performance** - Top sellers, trends
- **Agent analytics** - Performance tracking
- **Interactive charts** - Visual data exploration

### Data Management
- **CSV imports** - Bulk upload sales data
- **Agent management** - CRUD operations
- **Customer tracking** - Customer database
- **Product catalog** - 500+ products

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 14, React, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.9+ |
| **Database** | Supabase (PostgreSQL) |
| **AI/ML** | GROQ API (LLaMA 3.3 70B) |
| **Deployment** | Railway (Backend), Vercel (Frontend) |
| **Storage** | Supabase Storage |

---

## 📖 Documentation

- **[Quick Start Guide](./docs/QUICKSTART.md)** - Get up and running
- **[Deployment Guide](./docs/DEPLOYMENT.md)** - Deploy to production
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)** - Common issues
- **[AI Setup](./docs/guides/ai-setup.md)** - Configure AI assistant
- **[Database Setup](./docs/guides/database-setup.md)** - Set up Supabase

**Full documentation index:** [docs/README.md](./docs/README.md)

---

## 🔑 Environment Variables

Required environment variables (see [docs/examples/.env.example](./docs/examples/.env.example)):

**Backend (`backend/.env`):**
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key  
GROQ_API_KEY=your_groq_key
```

**Frontend (`frontend/.env.local`):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🧪 Testing

```bash
# Backend unit tests
cd backend
pytest

# Integration tests
cd tests/integration
python verify_backend.py

# Full test suite
./tests/integration/test_advanced_analytics.sh
```

See [tests/README.md](./tests/README.md) for details.

---

## 🚀 Deployment

**Backend (Railway):**
```bash
# Automatically deploys from main branch
git push origin main
```

**Frontend (Vercel):**
- Connected to GitHub repository
- Auto-deploys on push to main

**Manual deployment:** See [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)

---

## 📊 Database

**Migration:**
- Run SQL scripts from Supabase Dashboard
- Or use scripts in `database/migrations/`

**Seeds:**
- Sample data in `database/seeds/`
- Use for local development

**Schema:** See [database/README.md](./database/README.md)

---

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

---

## 📝 License

Proprietary - All rights reserved

---

## 🆘 Support

**Issues?** See [Troubleshooting Guide](./docs/TROUBLESHOOTING.md)

**Questions?** Check [documentation](./docs/README.md)

---

**Built for Belarus confectionery businesses 🍫**
