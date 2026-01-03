#!/bin/bash

# ============================================
# ALTERINI AI - Backend Startup Script
# ============================================

echo "🚀 Запуск Alterini AI Backend..."
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка .env файла
if [ ! -f .env ]; then
    echo -e "${RED}❌ Файл .env не найден!${NC}"
    echo ""
    echo "Выполни следующие шаги:"
    echo "  1. cp .env.example .env"
    echo "  2. Заполни все переменные в .env"
    echo "  3. Запусти ./start.sh снова"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Файл .env найден${NC}"

# Проверка виртуального окружения
if [ -d "venv" ]; then
    echo -e "${GREEN}✓ Виртуальное окружение найдено${NC}"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${GREEN}✓ Виртуальное окружение найдено${NC}"
    source .venv/bin/activate
else
    echo -e "${YELLOW}⚠ Виртуальное окружение не найдено${NC}"
    echo "  Создаю новое..."
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✓ Виртуальное окружение создано${NC}"
fi

# Установка зависимостей
echo ""
echo "📦 Проверка зависимостей..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Зависимости установлены${NC}"

# Проверка ключевых переменных
echo ""
echo "🔑 Проверка переменных окружения..."

source .env 2>/dev/null || export $(grep -v '^#' .env | xargs)

if [ -z "$SUPABASE_URL" ]; then
    echo -e "${RED}❌ SUPABASE_URL не установлен${NC}"
    exit 1
fi

if [ -z "$SUPABASE_KEY" ]; then
    echo -e "${RED}❌ SUPABASE_KEY не установлен${NC}"
    exit 1
fi

if [ -z "$GOOGLE_GEMINI_API_KEY" ]; then
    echo -e "${YELLOW}⚠ GOOGLE_GEMINI_API_KEY не установлен (AI функции будут недоступны)${NC}"
fi

echo -e "${GREEN}✓ Переменные окружения в порядке${NC}"

# Запуск сервера
echo ""
echo "============================================"
echo -e "${GREEN}🌐 Запуск сервера на http://localhost:8000${NC}"
echo "============================================"
echo ""
echo "📚 Документация: http://localhost:8000/docs"
echo "❤️ Health check: http://localhost:8000/health"
echo ""
echo "Нажми Ctrl+C для остановки"
echo ""

# Запуск uvicorn с hot reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
