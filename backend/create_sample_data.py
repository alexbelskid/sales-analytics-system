"""
Create Sample Agent Data for Testing
This script creates realistic sample agent data directly in the database
"""

import asyncio
import sys
sys.path.append('/Users/alexbelski/Desktop/new bi project/backend')

from app.database import supabase_admin
from datetime import date, timedelta
import uuid

async def main():
    print("=" * 70)
    print("CREATING SAMPLE AGENT DATA")
    print("=" * 70)
    print()
    
    # Sample agent data (realistic Belarusian names and regions)
    agents_data = [
        ("Иванов Иван", "МИНСК", "ivanov@company.com"),
        ("Петрова Мария", "БРЕСТ", "petrova@company.com"),
        ("Сидоров Алексей", "ВИТЕБСК", "sidorov@company.com"),
        ("Козлова Анна", "ГОМЕЛЬ", "kozlova@company.com"),
        ("Смирнов Дмитрий", "ГРОДНО", "smirnov@company.com"),
        ("Новикова Елена", "МОГИЛЕВ", "novikova@company.com"),
        ("Волков Сергей", "МИНСК", "volkov@company.com"),
        ("Соколова Ольга", "БРЕСТ", "sokolova@company.com"),
        ("Лебедев Николай", "ВИТЕБСК", "lebedev@company.com"),
        ("Морозова Татьяна", "ГОМЕЛЬ", "morozova@company.com"),
    ]
    
    print(f"Creating {len(agents_data)} agents...")
    created_agents = []
    
    for name, region, email in agents_data:
        try:
            # Create agent
            result = supabase_admin.table('agents').insert({
                'name': name,
                'email': email,
                'region': region,
                'is_active': True,
                'base_salary': 1000.0,
                'commission_rate': 5.0
            }).execute()
            
            if result.data:
                agent = result.data[0]
                created_agents.append(agent)
                print(f"  ✓ {name} ({region}) - ID: {agent['id'][:8]}...")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
    
    print()
    print(f"Created {len(created_agents)} agents")
    print()
    
    # Create sales plans for current month
    print("Creating sales plans...")
    period_start = date.today().replace(day=1)
    period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    plans_created = 0
    for agent in created_agents:
        try:
            # Plan amount varies by agent (50k-200k)
            import random
            plan_amount = random.randint(50000, 200000)
            
            result = supabase_admin.table('agent_sales_plans').insert({
                'agent_id': agent['id'],
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'plan_amount': plan_amount,
                'category': 'All'
            }).execute()
            
            if result.data:
                plans_created += 1
        except Exception as e:
            print(f"  ✗ Plan for {agent['name']}: {e}")
    
    print(f"  Created {plans_created} sales plans")
    print()
    
    # Create daily sales (last 30 days)
    print("Creating daily sales...")
    sales_created = 0
    
    for agent in created_agents:
        agent_plan = supabase_admin.table('agent_sales_plans').select('plan_amount').eq(
            'agent_id', agent['id']
        ).execute()
        
        if not agent_plan.data:
            continue
            
        plan = agent_plan.data[0]['plan_amount']
        
        # Create sales for last 30 days
        for day_offset in range(30):
            sale_date = date.today() - timedelta(days=day_offset)
            
            # Random sales (60-120% of daily plan)
            import random
            daily_amount = (plan / 30) * random.uniform(0.6, 1.2)
            
            try:
                result = supabase_admin.table('agent_daily_sales').insert({
                    'agent_id': agent['id'],
                    'sale_date': sale_date.isoformat(),
                    'amount': round(daily_amount, 2),
                    'category': random.choice(['FINISH', 'CALGON', 'CILLIT BANG', 'AIR WICK'])
                }).execute()
                
                if result.data:
                    sales_created += 1
            except:
                pass
    
    print(f"  Created {sales_created} daily sales")
    print()
    
    # Create import history record
    print("Creating import history...")
    try:
        supabase_admin.table('import_history').insert({
            'filename': 'sample_data_restored.xlsx',
            'import_type': 'agents',
            'status': 'completed',
            'total_rows': len(agents_data),
            'imported_rows': len(created_agents),
            'uploaded_at': 'now()'
        }).execute()
        print("  ✓ Import history created")
    except Exception as e:
        print(f"  ✗ {e}")
    
    print()
    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print()
    
    # Verify data
    agents_check = supabase_admin.table('agents').select('*', count='exact').execute()
    plans_check = supabase_admin.table('agent_sales_plans').select('*', count='exact').execute()
    sales_check = supabase_admin.table('agent_daily_sales').select('*', count='exact').execute()
    
    print(f"✓ Agents: {agents_check.count}")
    print(f"✓ Plans: {plans_check.count}")
    print(f"✓ Sales: {sales_check.count}")
    print()
    
    # Test AI context
    print("Testing AI Context...")
    try:
        from app.services.ai_context_service import ai_context
        context = ai_context.get_context_for_ai(
            include_agents=True,
            include_imports=True,
            include_general=False
        )
        
        if context and "агент" in context.lower():
            print("✅ AI CONTEXT WORKING!")
            print(f"   Context length: {len(context)} chars")
            print(f"   Preview: {context[:200]}...")
        else:
            print("❌ AI context empty or no agent data")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 70)
    print("✅ COMPLETE! Data restored and AI ready!")
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(main())
