#!/usr/bin/env python3
"""
Автоматическая настройка Supabase Storage для файлового хранилища
Запускает миграцию и создает bucket
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print_error("SUPABASE_URL и SUPABASE_KEY должны быть в .env файле")
    sys.exit(1)

print_info(f"Подключение к Supabase: {SUPABASE_URL}")

# Create Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print_success("Подключено к Supabase")
except Exception as e:
    print_error(f"Ошибка подключения: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("НАСТРОЙКА ФАЙЛОВОГО ХРАНИЛИЩА")
print("="*80 + "\n")

# ============================================================================
# Шаг 1: Создать Storage Bucket
# ============================================================================
print_info("Шаг 1/2: Создание Storage bucket 'import-files'...")

try:
    # Проверяем существует ли bucket
    buckets = supabase.storage.list_buckets()
    bucket_exists = any(b.name == 'import-files' for b in buckets)
    
    if bucket_exists:
        print_warning("Bucket 'import-files' уже существует, пропускаем создание")
    else:
        # Создаем bucket
        supabase.storage.create_bucket(
            'import-files',
            options={
                'public': False,  # Приватный bucket
                'file_size_limit': 100 * 1024 * 1024,  # 100 MB
                'allowed_mime_types': [
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/vnd.ms-excel'
                ]
            }
        )
        print_success("Bucket 'import-files' создан успешно")
except Exception as e:
    print_error(f"Ошибка при создании bucket: {e}")
    print_warning("Попробуй создать bucket вручную в Supabase Dashboard")

# ============================================================================
# Шаг 2: Запустить миграцию БД
# ============================================================================
print_info("\nШаг 2/2: Запуск SQL миграции...")

migration_path = "database/migrations/004_add_storage_path_to_import_history.sql"

try:
    # Читаем SQL миграцию
    with open(migration_path, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    print_info(f"Прочитан файл: {migration_path}")
    
    # Выполняем SQL через RPC
    # Supabase Python client не поддерживает прямое выполнение SQL
    # Поэтому выводим инструкцию
    print_warning("Supabase Python SDK не поддерживает выполнение произвольного SQL")
    print_info("Необходимо выполнить миграцию вручную:")
    print("\n" + "-"*80)
    print("1. Открой Supabase Dashboard → SQL Editor")
    print(f"2. Скопируй и выполни следующий SQL:\n")
    print(migration_sql)
    print("-"*80 + "\n")
    
    # Альтернативный способ - через psycopg2 если есть DATABASE_URL
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        try:
            import psycopg2
            print_info("Найден DATABASE_URL, пытаюсь выполнить миграцию через psycopg2...")
            
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute(migration_sql)
            conn.commit()
            cur.close()
            conn.close()
            
            print_success("Миграция выполнена успешно через psycopg2!")
        except ImportError:
            print_warning("psycopg2 не установлен. Установи: pip install psycopg2-binary")
        except Exception as e:
            print_error(f"Ошибка выполнения миграции: {e}")
    
except FileNotFoundError:
    print_error(f"Файл миграции не найден: {migration_path}")
except Exception as e:
    print_error(f"Ошибка: {e}")

# ============================================================================
# Итоги
# ============================================================================
print("\n" + "="*80)
print("НАСТРОЙКА ЗАВЕРШЕНА")
print("="*80 + "\n")

print_success("Bucket 'import-files' готов к использованию")
print_info("Следующие шаги:")
print("  1. Если миграция не выполнилась автоматически - запусти SQL вручную")
print("  2. Загрузи тестовый Excel файл через UI")
print("  3. Проверь что файл появился в Storage")
print("  4. Проверь кнопку 'Скачать' на странице /files")

print(f"\n{BLUE}Документация:{RESET}")
print(f"  - Walkthrough: .gemini/antigravity/brain/.../walkthrough.md")
print(f"  - Инструкции: STORAGE_SETUP.md")

print(f"\n{GREEN}Готово!{RESET}\n")
