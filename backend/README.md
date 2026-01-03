# Alterini AI - Backend

API сервер для аналитической системы продаж с AI-ассистентом.

## 🚀 Быстрый старт

```bash
# 1. Скопируй настройки окружения
cp .env.example .env

# 2. Заполни ключи в .env (инструкции внутри файла)

# 3. Запусти сервер
./start.sh
```

Сервер запустится на http://localhost:8000

## 📋 Переменные окружения

| Переменная | Описание | Где взять |
|------------|----------|-----------|
| `SUPABASE_URL` | URL вашего Supabase проекта | [Supabase Dashboard](https://supabase.com/dashboard) → Settings → API |
| `SUPABASE_KEY` | Anon/Public ключ | Там же |
| `GOOGLE_GEMINI_API_KEY` | API ключ для Gemini AI | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `DATABASE_URL` | PostgreSQL connection string | Supabase → Settings → Database → Connection string |

## 🔧 Ручной запуск

Если `start.sh` не работает:

```bash
# Создай виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установи зависимости
pip install -r requirements.txt

# Запусти сервер
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 Документация API

После запуска сервера открой в браузере:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔌 Список Endpoints

### Health & Info
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Информация о API |
| GET | `/health` | Проверка здоровья |
| GET | `/api/health` | Детальный health check |

### Analytics
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/analytics/dashboard` | Дашборд метрики |
| GET | `/api/analytics/sales-trend` | Тренд продаж |
| GET | `/api/analytics/top-products` | Топ товаров |
| GET | `/api/analytics/top-customers` | Топ клиентов |

### Data Upload
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/data/upload/sales` | Загрузка продаж (CSV) |
| POST | `/api/data/upload/products` | Загрузка товаров (CSV) |
| POST | `/api/data/upload/customers` | Загрузка клиентов (CSV) |
| GET | `/api/data/analytics/summary` | Сводка аналитики |

### AI Assistant
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/ai/generate-response` | Генерация ответа на email |
| GET | `/api/knowledge` | Список записей базы знаний |
| POST | `/api/knowledge` | Добавить запись |
| GET | `/api/training` | Список примеров обучения |
| POST | `/api/training` | Добавить пример |

### Forecast
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/forecast/predict` | Прогноз продаж |
| GET | `/api/forecast/seasonality` | Анализ сезонности |
| POST | `/api/forecast/train` | Обучение модели |

### Proposals
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/proposals/generate` | Генерация КП |
| POST | `/api/proposals/export/docx` | Экспорт в DOCX |
| POST | `/api/proposals/export/pdf` | Экспорт в PDF |

### Salary
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/salary/calculate` | Расчёт зарплат |

## 🧪 Тестирование

```bash
# Запусти тесты API (при работающем сервере)
python test_api.py
```

## 📁 Тестовые данные

В папке `test_data/` есть примеры CSV файлов:
- `sales_test.csv` - продажи
- `products_test.csv` - товары
- `customers_test.csv` - клиенты

## 🐛 Решение проблем

Смотри файл `TROUBLESHOOTING.md` в корне проекта.

## 🚢 Deploy на Railway

```bash
# Railway автоматически подхватит Dockerfile
railway up
```

Не забудь настроить переменные окружения в Railway Dashboard.

---

Made with ❤️ for Alterini AI
