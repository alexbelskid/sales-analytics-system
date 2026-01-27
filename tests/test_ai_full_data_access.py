"""
ТЕСТ: Проверка полного доступа AI к данным Supabase
=======================================================

Этот тест проверяет, что все 4 изменения работают корректно:
1. AI видит полный каталог данных
2. SQL генератор не ограничивает запросы жестким LIMIT
3. Классификатор правильно определяет запросы для INTERNAL_DB
4. Smart-loader загружает полные данные

Запуск: python tests/test_ai_full_data_access.py
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.unified_intelligence_service import unified_intelligence_service
from backend.app.services.sql_query_service import sql_query_service
from backend.app.services.enhanced_data_context_service import enhanced_data_context


async def test_step_1_data_catalog():
    """ТЕСТ ШАГ 1: Проверка загрузки полного каталога данных"""
    print("\n" + "="*80)
    print("📊 ТЕСТ ШАГ 1: Загрузка полного каталога данных")
    print("="*80)
    
    try:
        catalog = await enhanced_data_context.get_data_catalog()
        
        print(f"\n✅ Каталог успешно загружен:")
        print(f"   • Всего продаж: {catalog.total_sales:,}")
        print(f"   • Всего товаров: {catalog.total_products:,}")
        print(f"   • Всего клиентов: {catalog.total_customers:,}")
        print(f"   • Всего агентов: {catalog.total_agents:,}")
        print(f"   • Период данных: {catalog.date_range_start} - {catalog.date_range_end}")
        print(f"   • Категории ({len(catalog.categories)}): {', '.join(catalog.categories[:5])}")
        print(f"   • Регионы ({len(catalog.regions)}): {', '.join(catalog.regions)}")
        
        # Проверка что данные реальные
        assert catalog.total_sales > 0, "❌ Нет данных о продажах!"
        assert catalog.total_products > 0, "❌ Нет данных о товарах!"
        
        print("\n✅ ШАГ 1 ПРОЙДЕН: AI имеет доступ к полному каталогу данных!")
        return True
        
    except Exception as e:
        print(f"\n❌ ШАГ 1 ПРОВАЛЕН: {str(e)}")
        return False


async def test_step_2_sql_no_limit():
    """ТЕСТ ШАГ 2: Проверка что SQL не добавляет жесткий LIMIT для запросов 'все'"""
    print("\n" + "="*80)
    print("🔍 ТЕСТ ШАГ 2: SQL генератор без жестких лимитов")
    print("="*80)
    
    test_queries = [
        ("Покажи все товары", False),  # Должен быть БЕЗ LIMIT
        ("Топ 10 продуктов", True),    # Должен быть с LIMIT 10
        ("Сколько всего продаж?", False),  # COUNT - без LIMIT
    ]
    
    results = []
    
    for question, should_have_limit in test_queries:
        print(f"\n📝 Тестируем: '{question}'")
        
        try:
            result = await sql_query_service.generate_sql(question)
            
            if result["success"]:
                sql = result["sql"].upper()
                has_limit = "LIMIT" in sql
                
                print(f"   Сгенерированный SQL: {result['sql'][:100]}...")
                print(f"   Есть LIMIT: {has_limit}")
                
                if should_have_limit and not has_limit:
                    print(f"   ⚠️  ОЖИДАЛСЯ LIMIT, но его нет!")
                    results.append(False)
                elif not should_have_limit and has_limit:
                    print(f"   ⚠️  НЕ ОЖИДАЛСЯ LIMIT, но он есть!")
                    results.append(False)
                else:
                    print(f"   ✅ Правильно!")
                    results.append(True)
            else:
                print(f"   ❌ Ошибка генерации SQL: {result['error']}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Исключение: {str(e)}")
            results.append(False)
    
    if all(results):
        print("\n✅ ШАГ 2 ПРОЙДЕН: SQL корректно использует LIMIT!")
        return True
    else:
        print("\n⚠️  ШАГ 2 ЧАСТИЧНО ПРОЙДЕН: Некоторые запросы требуют доработки")
        return False


async def test_step_3_classification():
    """ТЕСТ ШАГ 3: Проверка улучшенной классификации запросов"""
    print("\n" + "="*80)
    print("🎯 ТЕСТ ШАГ 3: Улучшенная классификация запросов")
    print("="*80)
    
    test_cases = [
        ("Покажи все товары", "INTERNAL_DB"),
        ("Список всех агентов", "INTERNAL_DB"),
        ("Статистика продаж за год", "INTERNAL_DB"),
        ("Сколько товаров в категории молочные?", "INTERNAL_DB"),
        ("Привет!", "CHAT"),
    ]
    
    results = []
    
    for query, expected_type in test_cases:
        print(f"\n📝 Тестируем: '{query}'")
        print(f"   Ожидаемый тип: {expected_type}")
        
        try:
            classification = await unified_intelligence_service._classify_intent(query, [])
            actual_type = classification.get("type")
            confidence = classification.get("confidence", 0)
            reasoning = classification.get("reasoning", "")
            
            print(f"   Определен тип: {actual_type} (уверенность: {confidence:.2f})")
            print(f"   Обоснование: {reasoning[:100]}...")
            
            if actual_type == expected_type:
                print(f"   ✅ Правильно!")
                results.append(True)
            else:
                print(f"   ❌ Ошибка классификации!")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Исключение: {str(e)}")
            results.append(False)
    
    if all(results):
        print("\n✅ ШАГ 3 ПРОЙДЕН: Классификация работает корректно!")
        return True
    else:
        print("\n⚠️  ШАГ 3 ЧАСТИЧНО ПРОЙДЕН: Некоторые запросы классифицированы неверно")
        return False


async def test_step_4_smart_loader():
    """ТЕСТ ШАГ 4: Проверка smart-loader для полной загрузки данных"""
    print("\n" + "="*80)
    print("🚀 ТЕСТ ШАГ 4: Smart-loader для полной загрузки данных")
    print("="*80)
    
    test_queries = [
        "Покажи все товары категории молочные",
        "Список всех агентов региона Минск",
        "Все клиенты",
    ]
    
    results = []
    
    for query in test_queries:
        print(f"\n📝 Тестируем: '{query}'")
        
        try:
            data = await enhanced_data_context.get_complete_data_for_ai_query(query)
            
            # Проверяем что данные загружены
            has_data = len(data) > 500  # Должно быть много текста
            has_full_access_marker = "ПОЛН" in data or "ВСЕ" in data
            
            print(f"   Размер ответа: {len(data)} символов")
            print(f"   Маркер полного доступа: {has_full_access_marker}")
            print(f"   Превью: {data[:200]}...")
            
            if has_data and has_full_access_marker:
                print(f"   ✅ Данные загружены полностью!")
                results.append(True)
            else:
                print(f"   ⚠️  Данные могут быть неполными")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Исключение: {str(e)}")
            results.append(False)
    
    if all(results):
        print("\n✅ ШАГ 4 ПРОЙДЕН: Smart-loader работает корректно!")
        return True
    else:
        print("\n⚠️  ШАГ 4 ЧАСТИЧНО ПРОЙДЕН: Некоторые запросы требуют доработки")
        return False


async def test_full_integration():
    """ИНТЕГРАЦИОННЫЙ ТЕСТ: Проверка работы всей системы"""
    print("\n" + "="*80)
    print("🎯 ИНТЕГРАЦИОННЫЙ ТЕСТ: Полный запрос через AI агента")
    print("="*80)
    
    test_query = "Покажи полный список всех товаров"
    
    print(f"\n📝 Отправляем запрос: '{test_query}'")
    
    try:
        import uuid
        session_id = str(uuid.uuid4())
        
        result = await unified_intelligence_service.process_message(session_id, test_query)
        
        print(f"\n✅ Результат получен:")
        print(f"   • Тип классификации: {result.get('classification', {}).get('type')}")
        print(f"   • SQL выполнен: {result.get('debug_sql', {}).get('success')}")
        print(f"   • Количество записей: {result.get('debug_sql', {}).get('row_count', 0)}")
        print(f"\n📄 Ответ AI:")
        print("-" * 80)
        print(result.get('response', '')[:500])
        print("-" * 80)
        
        # Проверки
        classification_correct = result.get('classification', {}).get('type') == 'INTERNAL_DB'
        has_sql_data = result.get('debug_sql', {}).get('success') == True
        
        if classification_correct and has_sql_data:
            print("\n✅ ИНТЕГРАЦИОННЫЙ ТЕСТ ПРОЙДЕН!")
            return True
        else:
            print("\n⚠️  ИНТЕГРАЦИОННЫЙ ТЕСТ ЧАСТИЧНО ПРОЙДЕН")
            return False
            
    except Exception as e:
        print(f"\n❌ ИНТЕГРАЦИОННЫЙ ТЕСТ ПРОВАЛЕН: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Запуск всех тестов"""
    print("\n" + "="*80)
    print("🧪 ТЕСТИРОВАНИЕ: AI ПОЛНЫЙ ДОСТУП К ДАННЫМ SUPABASE")
    print("="*80)
    print("\nПроверяем все 4 шага изменений:\n")
    print("  ШАГ 1: Подключение полного каталога данных")
    print("  ШАГ 2: Убраны жесткие LIMIT в SQL")
    print("  ШАГ 3: Улучшенная классификация запросов")
    print("  ШАГ 4: Smart-loader для полной загрузки данных")
    
    results = {}
    
    # Запуск всех тестов
    results['step_1'] = await test_step_1_data_catalog()
    results['step_2'] = await test_step_2_sql_no_limit()
    results['step_3'] = await test_step_3_classification()
    results['step_4'] = await test_step_4_smart_loader()
    results['integration'] = await test_full_integration()
    
    # Итоговый отчет
    print("\n" + "="*80)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ ПРОЙДЕН" if passed else "❌ ПРОВАЛЕН"
        print(f"{test_name:20s}: {status}")
    
    total_passed = sum(1 for v in results.values() if v)
    total_tests = len(results)
    
    print("\n" + "="*80)
    print(f"Всего тестов: {total_tests}")
    print(f"Пройдено: {total_passed}")
    print(f"Провалено: {total_tests - total_passed}")
    print("="*80)
    
    if total_passed == total_tests:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! AI ИМЕЕТ ПОЛНЫЙ ДОСТУП К ДАННЫМ!")
    else:
        print(f"\n⚠️  {total_passed}/{total_tests} тестов пройдено. Требуется доработка.")


if __name__ == "__main__":
    asyncio.run(main())
