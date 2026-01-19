"""
Test and Fix Script for Agent Data Import
Fixes the RLS issue and re-imports existing agent data
"""

import asyncio
import sys
sys.path.append('/Users/alexbelski/Desktop/new bi project/backend')

from app.database import supabase, supabase_admin
from app.services.google_sheets_importer import google_sheets_importer

async def main():
    print("=" * 60)
    print("AGENT DATA IMPORT FIX & TEST")
    print("=" * 60)
    print()
    
    # Step 1: Check current state
    print("STEP 1: Checking current database state...")
    agents = supabase.table('agents').select('*', count='exact').execute()
    plans = supabase.table('agent_sales_plans').select('*', count='exact').execute()
    sales = supabase.table('agent_daily_sales').select('*', count='exact').execute()
    
    print(f"  Agents: {agents.count} records")
    print(f"  Plans: {plans.count} records")
    print(f"  Sales: {sales.count} records")
    print()
    
    # Step 2: Get unique agent_ids from plans
    print("STEP 2: Extracting unique agent IDs from existing plans...")
    unique_agent_ids = set()
    agent_regions = {}
    
    for plan in plans.data:
        agent_id = plan['agent_id']
        unique_agent_ids.add(agent_id)
        # Try to guess region from somewhere (if available)
        if 'region' in plan:
            agent_regions[agent_id] = plan.get('region', 'МИНСК')
    
    print(f"  Found {len(unique_agent_ids)} unique agent IDs")
    print()
    
    # Step 3: Create missing agents
    print("STEP 3: Creating missing agent records...")
    created_count = 0
    failed_count = 0
    
    for idx, agent_id in enumerate(unique_agent_ids, 1):
        print(f"  [{idx}/{len(unique_agent_ids)}] Processing agent {agent_id[:8]}...", end=' ')
        
        # Check if already exists
        existing = supabase_admin.table('agents').select('id').eq('id', agent_id).execute()
        if existing.data:
            print("✓ Already exists")
            continue
        
        # Create agent with placeholder name
        try:
            result = supabase_admin.table('agents').insert({
                'id': agent_id,  # Use existing UUID
                'name': f'Agent {idx}',  # Placeholder - will be updated on next import
                'email': f'agent{idx}@company.com',
                'region': agent_regions.get(agent_id, 'МИНСК'),
                'is_active': True
            }).execute()
            
            if result.data:
                print("✅ Created")
                created_count += 1
            else:
                print("❌ Failed (no data returned)")
                failed_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            failed_count += 1
    
    print()
    print(f"  Created: {created_count}")
    print(f"  Failed: {failed_count}")
    print()
    
    # Step 4: Verify
    print("STEP 4: Verifying database state...")
    agents_after = supabase.table('agents').select('*', count='exact').execute()
    print(f"  Agents now: {agents_after.count} records")
    print()
    
    # Step 5: Test AI context
    print("STEP 5: Testing AI context service...")
    try:
        from app.services.ai_context_service import ai_context
        context = ai_context.get_context_for_ai(
            include_agents=True,
            include_imports=True,
            include_general=False
        )
        
        if "агентов" in context.lower() and agents_after.count > 0:
            print("  ✅ AI context shows agent data!")
            print(f"  Context preview: {context[:300]}...")
        else:
            print("  ❌ AI context still shows no agents")
    except Exception as e:
        print(f"  ❌ Error getting context: {e}")
    
    print()
    print("=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Re-import your Excel file to update agent names")
    print("2. Agent names will be updated with real names from file")
    print("3. AI will now be able to answer questions about agents!")

if __name__ == '__main__':
    asyncio.run(main())
