#!/usr/bin/env python3
"""
Alterini AI - API Testing Script
================================

Запусти этот скрипт когда backend работает локально:
    python test_api.py

Требования:
    - Backend запущен на http://localhost:8000
    - pip install requests
"""

import requests
import os
import sys

BASE_URL = "http://localhost:8000"

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_header(text):
    print(f"\n{Colors.BLUE}{'='*50}{Colors.END}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'='*50}{Colors.END}")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def test_health():
    """Тест health endpoint"""
    print_header("1. Проверка Health Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check пройден")
            print(f"   Status: {data.get('status')}")
            print(f"   Environment: {data.get('environment')}")
            return True
        else:
            print_error(f"Неожиданный статус: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Не удалось подключиться к серверу!")
        print_warning("Убедись что backend запущен: ./start.sh")
        return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False


def test_root():
    """Тест корневого endpoint"""
    print_header("2. Проверка Root Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Root endpoint работает")
            print(f"   Name: {data.get('name')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Docs: {BASE_URL}{data.get('docs')}")
            return True
        else:
            print_error(f"Статус: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False


def test_analytics():
    """Тест аналитики"""
    print_header("3. Проверка Analytics API")
    
    try:
        response = requests.get(f"{BASE_URL}/api/data/analytics/summary", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_success("Analytics summary получен")
            
            if 'monthly' in data:
                monthly = data['monthly']
                print(f"   Revenue: {monthly.get('revenue', 0)} BYN")
                print(f"   Orders: {monthly.get('orders', 0)}")
                print(f"   Customers: {monthly.get('customers', 0)}")
            
            if 'knowledge' in data:
                print(f"   Knowledge entries: {data['knowledge'].get('total', 0)}")
            
            return True
        else:
            print_warning(f"Статус: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False


def test_csv_upload():
    """Тест загрузки CSV"""
    print_header("4. Проверка CSV Upload")
    
    csv_path = os.path.join(os.path.dirname(__file__), 'test_data', 'sales_test.csv')
    
    if not os.path.exists(csv_path):
        print_warning(f"Тестовый файл не найден: {csv_path}")
        return False
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'file': ('sales_test.csv', f, 'text/csv')}
            data = {'mode': 'append'}
            response = requests.post(
                f"{BASE_URL}/api/data/upload/sales",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print_success("CSV успешно загружен")
            print(f"   Total: {result.get('total', 'N/A')}")
            print(f"   Imported: {result.get('imported', 'N/A')}")
            print(f"   Skipped: {result.get('skipped', 'N/A')}")
            return True
        else:
            print_warning(f"Статус: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False


def test_email_generation():
    """Тест генерации ответа на email"""
    print_header("5. Проверка AI Email Generation")
    
    payload = {
        "email_from": "client@example.com",
        "email_subject": "Вопрос о продукции",
        "email_body": "Добрый день! Хотел бы узнать цены на торты для корпоратива на 50 человек.",
        "tone": "professional"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/generate-response",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Email ответ сгенерирован")
            
            generated = result.get('generated_response', '')[:150]
            print(f"   Ответ: {generated}...")
            return True
        else:
            print_warning(f"Статус: {response.status_code}")
            if response.status_code == 500:
                print_warning("   Возможно не настроен GOOGLE_GEMINI_API_KEY")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False


def test_knowledge_base():
    """Тест базы знаний"""
    print_header("6. Проверка Knowledge Base")
    
    try:
        response = requests.get(f"{BASE_URL}/api/knowledge", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else 0
            print_success(f"Knowledge base доступна")
            print(f"   Записей: {count}")
            return True
        else:
            print_warning(f"Статус: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        return False


def main():
    print(f"\n{Colors.BLUE}{'='*50}{Colors.END}")
    print(f"{Colors.BLUE}   ALTERINI AI - API Testing Script{Colors.END}")
    print(f"{Colors.BLUE}{'='*50}{Colors.END}")
    print(f"\nТестирование: {BASE_URL}")
    
    results = []
    
    # Сначала проверяем подключение
    if not test_health():
        print(f"\n{Colors.RED}{'='*50}{Colors.END}")
        print(f"{Colors.RED}Backend недоступен! Запусти его командой:{Colors.END}")
        print(f"{Colors.YELLOW}   cd backend && ./start.sh{Colors.END}")
        print(f"{Colors.RED}{'='*50}{Colors.END}\n")
        sys.exit(1)
    
    results.append(("Health", True))
    results.append(("Root", test_root()))
    results.append(("Analytics", test_analytics()))
    results.append(("CSV Upload", test_csv_upload()))
    results.append(("Email AI", test_email_generation()))
    results.append(("Knowledge", test_knowledge_base()))
    
    # Итоги
    print_header("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
    
    print(f"\n{Colors.BLUE}Пройдено: {passed}/{total}{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}🎉 Все тесты пройдены!{Colors.END}\n")
    else:
        print(f"\n{Colors.YELLOW}⚠ Некоторые тесты не пройдены{Colors.END}")
        print(f"{Colors.YELLOW}  Проверь настройки в .env файле{Colors.END}\n")


if __name__ == "__main__":
    main()
