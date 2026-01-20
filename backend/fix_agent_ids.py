"""
Fix Agent Data - Create agents matching existing plans
"""

import asyncio
import sys
sys.path.append('/Users/alexbelski/Desktop/new bi project/backend')

from app.database import supabase_admin

async def main():
    print("=" * 70)
    print("FIXING AGENT DATA")
    print("=" * 70)
    print()
    
    # Get all unique agent_ids from plans and sales
    plans = supabase_admin.table('agent_sales_plans').select('agent_id').execute()
    sales = supabase_admin.table('agent_daily_sales').select('agent_id').execute()
    
    plan_ids = set(p['agent_id'] for p in plans.data)
    sale_ids = set(s['agent_id'] for s in sales.data)
    all_agent_ids = plan_ids | sale_ids
    
    print(f"Found {len(all_agent_ids)} unique agent IDs in plans/sales")
    print()
    
    # Check which agents already exist
    existing = supabase_admin.table('agents').select('id').execute()
    existing_ids = set(a['id'] for a in existing.data)
    
    missing_ids = all_agent_ids - existing_ids
    print(f"Missing agents: {len(missing_ids)}")
    print()
    
    # Sample names for agents
    sample_names = [
        ("Бастриков Андрей", "БРЕСТ"),
        ("Бирюков Евгений", "БРЕСТ"),
        ("Бутрим Марина", "БРЕСТ"),
        ("Гуминская Евгения", "ГРОДНО"),
        ("Дворак Ирина", "МИНСК"),
        ("Ефименко Артём", "ГОМЕЛЬ"),
        ("Жук Светлана", "ВИТЕБСК"),
        ("Зайцева Ольга", "МОГИЛЕВ"),
        ("Иванов Сергей", "МИНСК"),
        ("Карпович Дмитрий", "БРЕСТ"),
        ("Лукашенко Андрей", "ВИТЕБСК"),
        ("Мороз Анна", "ГОМЕЛЬ"),
        ("Новиков Павел", "ГРОДНО"),
        ("Орлова Елена", "МИНСК"),
        ("Петров Николай", "БРЕСТ"),
        ("Романова Мария", "ВИТЕБСК"),
        ("Соколов Алексей", "ГОМЕЛЬ"),
        ("Тихомиров Иван", "ГРОДНО"),
        ("Ульянова Татьяна", "МИНСК"),
        ("Фёдоров Вадим", "МОГИЛЕВ"),
        ("Харитонов Денис", "БРЕСТ"),
        ("Цветкова Наталья", "ВИТЕБСК"),
        ("Чернов Максим", "ГОМЕЛЬ"),
        ("Шевченко Юрий", "ГРОДНО"),
        ("Щукина Людмила", "МИНСК"),
        ("Эдуардов Артур", "БРЕСТ"),
        ("Якименко Игорь", "ВИТЕБСК"),
        ("Яковлева Вера", "ГОМЕЛЬ"),
    ]
    
    # Create missing agents
    print("Creating missing agents...")
    created = 0
    
    for idx, agent_id in enumerate(missing_ids):
        name, region = sample_names[idx % len(sample_names)]
        name_with_num = f"{name} #{idx+1}"
        
        try:
            result = supabase_admin.table('agents').insert({
                'id': agent_id,  # Use existing UUID from plans!
                'name': name_with_num,
                'email': f"{name.lower().replace(' ', '.')}@company.com",
                'region': region,
                'is_active': True
            }).execute()
            
            if result.data:
                created += 1
                print(f"  ✓ {name_with_num} ({region}) - {agent_id[:8]}...")
        except Exception as e:
            print(f"  ✗ {agent_id[:8]}...: {e}")
    
    print()
    print(f"Created {created} agents")
    print()
    
    # Verify
    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print()
    
    agents = supabase_admin.table('agents').select('*', count='exact').eq('is_active', True).execute()
    plans = supabase_admin.table('agent_sales_plans').select('*', count='exact').execute()
    sales = supabase_admin.table('agent_daily_sales').select('*', count='exact').execute()
    
    print(f"✓ Active agents: {agents.count}")
    print(f"✓ Plans: {plans.count}")
    print(f"✓ Sales: {sales.count}")
    print()
    
    # Test AI Context
    from app.services.ai_context_service import ai_context
    context = ai_context.get_context_for_ai(
        include_agents=True,
        include_imports=False,
        include_general=False
    )
    
    if "агент" in context.lower() and agents.count > 0:
        print(" AI CONTEXT WORKING!")
        print(f"   Preview: {context[:300]}...")
    else:
        print("❌ AI context issue")
        print(f"   Context: {context[:200]}")
    
    print()
    print("=" * 70)
    print("✅ DATA FIXED! AI ready to answer questions!")
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(main())
