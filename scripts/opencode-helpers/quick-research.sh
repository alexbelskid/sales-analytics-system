#!/bin/bash

# ========================================
# Быстрое исследование через агентов
# ========================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

if [ -z "$1" ]; then
    echo "Использование: ./quick-research.sh <тип> \"Вопрос\""
    echo ""
    echo "Типы исследования:"
    echo "  solution   - Исследование решений и best practices"
    echo "  codebase   - Исследование существующего кода"
    echo "  web        - Поиск в интернете (документация, примеры)"
    echo ""
    echo "Примеры:"
    echo "  ./quick-research.sh solution \"Как реализовать OAuth в FastAPI?\""
    echo "  ./quick-research.sh codebase \"Как работает аутентификация?\""
    echo "  ./quick-research.sh web \"FastAPI best practices 2024\""
    exit 1
fi

TYPE="$1"
QUESTION="$2"

case "$TYPE" in
    solution)
        AGENT="research-solution"
        ;;
    codebase)
        AGENT="research-codebase"
        ;;
    web)
        AGENT="research-web"
        ;;
    *)
        echo "❌ Неизвестный тип: $TYPE"
        echo "Доступные: solution, codebase, web"
        exit 1
        ;;
esac

echo ""
print_step "🔍 БЫСТРОЕ ИССЛЕДОВАНИЕ"
echo ""
echo "Тип: $TYPE"
echo "Вопрос: $QUESTION"
echo ""

print_step "Промпт для OpenCode:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << EOF
@$AGENT

$QUESTION
EOF
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_warning "Скопируй этот промпт в OpenCode"
