#!/bin/bash

# Скрипт для запуска всех процессов приложения
# Usage: ./start.sh

set -e

PROJECT_DIR="/Users/alexbelski/Desktop/new bi project"
cd "$PROJECT_DIR"

echo "🚀 Запуск всех процессов приложения..."
echo ""

# Очистка старых процессов
echo "🧹 Очистка старых процессов..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Запуск бэкенда (FastAPI)
echo "🔧 Запуск бэкенда на http://127.0.0.1:8000 ..."
cd "$PROJECT_DIR/backend"
source "$PROJECT_DIR/.venv/bin/activate"
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload > "$PROJECT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "   ✅ Бэкенд запущен (PID: $BACKEND_PID)"
cd "$PROJECT_DIR"

# Ожидание запуска бэкенда
sleep 3

# Запуск фронтенда (Next.js)
echo "🎨 Запуск фронтенда на http://localhost:3000 ..."
cd "$PROJECT_DIR/frontend"
nohup npm run dev > "$PROJECT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "   ✅ Фронтенд запущен (PID: $FRONTEND_PID)"
cd "$PROJECT_DIR"

# Ожидание запуска фронтенда
sleep 5

echo ""
echo "✨ Все процессы запущены!"
echo ""
echo "📊 Статус:"
echo "   • Бэкенд:  http://127.0.0.1:8000 (PID: $BACKEND_PID)"
echo "   • Swagger: http://127.0.0.1:8000/docs"
echo "   • Фронтенд: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "📋 Логи:"
echo "   • Бэкенд:  tail -f $PROJECT_DIR/backend.log"
echo "   • Фронтенд: tail -f $PROJECT_DIR/frontend.log"
echo ""
echo "🛑 Остановить все процессы:"
echo "   ./stop.sh"
echo ""
