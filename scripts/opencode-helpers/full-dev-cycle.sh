#!/bin/bash

# ========================================
# OpenCode Agent Automation Script
# Полный цикл разработки новой функции
# ========================================

set -e

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция для красивого вывода
print_step() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Проверка аргументов
if [ -z "$1" ]; then
    print_error "Использование: ./full-dev-cycle.sh \"Описание задачи\""
    echo ""
    echo "Пример:"
    echo "  ./full-dev-cycle.sh \"Создать API для управления пользователями\""
    exit 1
fi

TASK_DESCRIPTION="$1"

echo ""
print_step "🚀 АВТОМАТИЗИРОВАННЫЙ ЦИКЛ РАЗРАБОТКИ"
echo ""
echo "Задача: $TASK_DESCRIPTION"
echo ""

# ШАГ 1: Исследование
print_step "ШАГ 1/4: Исследование решения (@research-solution)"
print_warning "Сейчас будет запущен агент исследования..."
echo ""
echo "Промпт для OpenCode:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << EOF
@research-solution

Задача: $TASK_DESCRIPTION

Проведи исследование:
1. Какие технологии и библиотеки использовать?
2. Какие есть готовые решения и best practices?
3. Какие подводные камни могут возникнуть?
4. Какую архитектуру выбрать?
5. Дай пошаговый план реализации

Учти существующий стек проекта (проверь package.json, requirements.txt).
EOF
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_warning "Скопируй этот промпт в OpenCode и выполни."
read -p "Нажми Enter когда исследование будет готово..."

# ШАГ 2: Архитектура
print_step "ШАГ 2/4: Проектирование архитектуры (@architecture-designer)"
echo ""
echo "Промпт для OpenCode:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << EOF
@architecture-designer

На основе результатов исследования спроектируй архитектуру для задачи:
$TASK_DESCRIPTION

Требования:
1. Интеграция с существующим кодом
2. Следование паттернам проекта
3. Создай диаграммы (sequence, class diagrams)
4. Опиши все компоненты и их взаимодействие
5. Сохрани ADR в docs/arch/decisions/

Проверь существующую архитектуру через @research-codebase если нужно.
EOF
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_warning "Скопируй этот промпт в OpenCode и выполни."
read -p "Нажми Enter когда архитектура будет готова..."

# ШАГ 3: Декомпозиция
print_step "ШАГ 3/4: Разбиение на задачи (@decomposition)"
echo ""
echo "Промпт для OpenCode:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << EOF
@decomposition

Разбей реализацию на задачи:
$TASK_DESCRIPTION

Требования:
1. Используй созданную архитектуру (проверь docs/arch/decisions/)
2. Каждая задача: 30 минут - 4 часа
3. Укажи зависимости между задачами
4. Создай файлы в docs/tasks/
5. Включи tasks для тестов
6. Убедись что все требования покрыты

Сделай задачи понятными для новичка.
EOF
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_warning "Скопируй этот промпт в OpenCode и выполни."
read -p "Нажми Enter когда декомпозиция будет готова..."

# ШАГ 4: Разработка
print_step "ШАГ 4/4: Разработка (Developer агенты)"
echo ""
print_warning "Теперь выполняй задачи по очереди с помощью скрипта execute-task.sh"
echo ""
echo "Пример:"
echo "  ./scripts/opencode-helpers/execute-task.sh 001"
echo ""

print_success "Автоматизированный цикл настроен!"
echo ""
echo "Следующие шаги:"
echo "  1. Используй ./execute-task.sh для выполнения каждой задачи"
echo "  2. Каждая задача = 1 коммит"
echo "  3. После всех задач используй ./finish-feature.sh"
echo ""
