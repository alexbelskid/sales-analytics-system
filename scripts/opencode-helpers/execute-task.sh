#!/bin/bash

# ========================================
# Выполнение отдельной задачи с автокоммитом
# ========================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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
    print_error "Использование: ./execute-task.sh <номер_задачи> [язык]"
    echo ""
    echo "Примеры:"
    echo "  ./execute-task.sh 001 python"
    echo "  ./execute-task.sh 005 csharp"
    echo "  ./execute-task.sh 003 typescript"
    echo ""
    echo "Если язык не указан, используется python по умолчанию"
    exit 1
fi

TASK_NUMBER="$1"
LANGUAGE="${2:-python}"

# Определение агента
case "$LANGUAGE" in
    python|py)
        AGENT="python-senior-developer"
        ;;
    csharp|cs|c#)
        AGENT="csharp-senior-developer"
        ;;
    typescript|ts|vue)
        AGENT="typescript-vue-developer"
        ;;
    *)
        print_error "Неизвестный язык: $LANGUAGE"
        echo "Доступные: python, csharp, typescript"
        exit 1
        ;;
esac

echo ""
print_step "🔨 ВЫПОЛНЕНИЕ ЗАДАЧИ #$TASK_NUMBER"
echo ""

# Поиск файла задачи
TASK_FILE=$(find docs/tasks -name "task-${TASK_NUMBER}-*.md" 2>/dev/null | head -n 1)

if [ -z "$TASK_FILE" ]; then
    print_error "Файл задачи task-${TASK_NUMBER}-*.md не найден в docs/tasks/"
    echo ""
    echo "Доступные задачи:"
    find docs/tasks -name "task-*.md" 2>/dev/null | sort
    exit 1
fi

print_success "Найдена задача: $TASK_FILE"
echo ""

# Генерация промпта
print_step "Промпт для OpenCode:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat << EOF
@$AGENT

Выполни задачу из файла: $TASK_FILE

Требования:
1. Внимательно прочитай описание задачи
2. Изучи существующий код (используй grep/glob/read)
3. Следуй паттернам проекта
4. Напиши чистый, понятный код
5. Добавь type hints (для Python) или строгую типизацию
6. Обработай ошибки
7. Напиши тесты если требуется
8. Убедись что код компилируется/запускается

После завершения дай краткий отчет о сделанном.
EOF
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_warning "Скопируй этот промпт в OpenCode и выполни."
read -p "Нажми Enter когда задача будет выполнена..."

# Проверка изменений
print_step "Проверка изменений"
echo ""

if ! git diff --quiet || ! git diff --cached --quiet; then
    print_success "Обнаружены изменения в файлах"
    echo ""
    echo "Измененные файлы:"
    git status --short
    echo ""
    
    # Запрос имени коммита
    TASK_NAME=$(basename "$TASK_FILE" .md | sed 's/task-[0-9]*-//')
    DEFAULT_COMMIT_MSG="Task #$TASK_NUMBER: $TASK_NAME"
    
    echo "Предложенное сообщение коммита:"
    echo "  $DEFAULT_COMMIT_MSG"
    echo ""
    read -p "Нажми Enter чтобы использовать или введи свое: " CUSTOM_MSG
    
    if [ -z "$CUSTOM_MSG" ]; then
        COMMIT_MSG="$DEFAULT_COMMIT_MSG"
    else
        COMMIT_MSG="$CUSTOM_MSG"
    fi
    
    # Коммит
    git add .
    git commit -m "$COMMIT_MSG"
    
    print_success "Изменения закоммичены: $COMMIT_MSG"
else
    print_warning "Изменений не обнаружено"
fi

echo ""
print_success "Задача #$TASK_NUMBER завершена!"
echo ""
echo "Следующие шаги:"
echo "  - Выполни следующую задачу: ./execute-task.sh $(printf "%03d" $((10#$TASK_NUMBER + 1))) $LANGUAGE"
echo "  - Или запусти тесты: pytest / npm test"
echo ""
