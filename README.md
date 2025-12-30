# Sales Analytics System

Система аналитики продаж с AI-автоматизацией для B2B бизнеса.

## 🚀 Возможности

- **📊 Дашборд аналитики** — выручка, средний чек, топ клиентов/товаров
- **📁 Импорт данных** — загрузка из Excel/CSV
- **✉️ AI автоответы** — генерация ответов на письма (GPT-4)
- **📄 Коммерческие предложения** — создание КП с экспортом в DOCX/PDF
- **🔮 ML прогнозирование** — предсказание продаж (Prophet)
- **💰 Расчёт зарплат** — оклад + % от продаж + бонусы

## 🛠 Технологии

| Backend | Frontend | Database |
|---------|----------|----------|
| FastAPI | Next.js 14 | PostgreSQL |
| Python 3.11+ | React 18 | Supabase |
| Pydantic | Recharts | |
| Prophet (ML) | Tailwind CSS | |

## 📦 Быстрый старт

### Docker (рекомендуется)
```bash
cp .env.example .env
# Заполнить: SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY

docker-compose up -d
```

### Локально
```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install && npm run dev
```

## 🔗 URLs

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs

## 📚 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | Основные метрики |
| GET | `/api/analytics/top-customers` | Топ клиентов |
| GET | `/api/analytics/sales-trend` | Динамика продаж |
| POST | `/api/upload/excel` | Загрузка Excel/CSV |
| POST | `/api/email/generate-reply` | AI генерация ответа |
| POST | `/api/proposals/generate` | Создание КП |
| GET | `/api/forecast/predict` | ML прогноз |
| GET | `/api/salary/calculate` | Расчёт зарплат |

## 📁 Структура

```
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── routers/
│   │   └── services/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   └── package.json
├── supabase/
│   └── migrations/
└── docker-compose.yml
```

## ⚙️ Настройка

1. **Supabase**: Создать проект на [supabase.com](https://supabase.com)
2. **Миграция**: Применить `supabase/migrations/001_initial_schema.sql`
3. **OpenAI**: Получить API ключ на [platform.openai.com](https://platform.openai.com)
4. **`.env`**: Заполнить переменные окружения

## 📄 Лицензия

MIT
