"""
AI Brain Configuration Test
Tests the enhanced system prompts and knowledge management
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.unified_intelligence_service import unified_intelligence_service
from app.services.company_knowledge_service import company_knowledge_service


async def test_strategic_analysis():
    """Test: Strategic analysis with Belarus context"""
    print("\n" + "="*80)
    print("TEST 1: Strategic Analysis - Should AI recommend expanding to Brest?")
    print("="*80)
    
    session_id = "test_session_1"
    question = "Стоит ли нам расширяться в Брест?"
    
    print(f"\nQuestion: {question}")
    print("\nExpected behavior:")
    print("1. Check internal DB for Brest sales data")
    print("2. Search web for Brest economic conditions")
    print("3. Provide strategic recommendation with Belarus context")
    
    result = await unified_intelligence_service.process_message(session_id, question)
    
    print(f"\n--- CLASSIFICATION ---")
    print(f"Type: {result['classification'].get('type')}")
    print(f"Reasoning: {result['classification'].get('reasoning')}")
    
    print(f"\n--- SOURCES USED ---")
    for source in result['sources']:
        print(f"- {source['type'].upper()}: {source['status']}")
    
    print(f"\n--- AI RESPONSE ---")
    print(result['response'])
    
    return result


async def test_memory_injection():
    """Test: Memory injection - teaching new facts"""
    print("\n" + "="*80)
    print("TEST 2: Memory Injection - Teaching AI about new warehouse")
    print("="*80)
    
    # Teach a fact
    fact = "В Гродно у нас теперь новый склад на 500 кв.м."
    print(f"\nTeaching fact: {fact}")
    
    new_fact = company_knowledge_service.add_fact(
        fact=fact,
        category="logistics",
        created_by="test"
    )
    
    print(f"✓ Fact saved with ID: {new_fact['id']}")
    
    # Verify it's in the context
    context = company_knowledge_service.get_context_for_ai()
    print(f"\n--- COMPANY CONTEXT (excerpt) ---")
    print(context[:500] + "...")
    
    # Ask about warehouses
    session_id = "test_session_2"
    question = "Где у нас склады?"
    
    print(f"\n\nQuestion: {question}")
    print("Expected: AI should mention the new Grodno warehouse")
    
    result = await unified_intelligence_service.process_message(session_id, question)
    
    print(f"\n--- AI RESPONSE ---")
    print(result['response'])
    
    # Check if Grodno is mentioned
    if "Гродно" in result['response'] or "Grodno" in result['response']:
        print("\n✓ SUCCESS: AI mentioned Grodno warehouse!")
    else:
        print("\n✗ WARNING: AI did not mention Grodno warehouse")
    
    return result


async def test_belarus_expertise():
    """Test: Belarus market expertise"""
    print("\n" + "="*80)
    print("TEST 3: Belarus Market Expertise - Tax and regional knowledge")
    print("="*80)
    
    session_id = "test_session_3"
    question = "Какие налоги на продажи в РБ?"
    
    print(f"\nQuestion: {question}")
    print("Expected: AI should mention 20% VAT")
    
    result = await unified_intelligence_service.process_message(session_id, question)
    
    print(f"\n--- AI RESPONSE ---")
    print(result['response'])
    
    # Check for VAT mention
    if "20" in result['response'] and ("НДС" in result['response'] or "VAT" in result['response']):
        print("\n✓ SUCCESS: AI correctly stated 20% VAT!")
    else:
        print("\n✗ WARNING: AI did not mention 20% VAT")
    
    return result


async def test_data_priority():
    """Test: Data priority - DB first, then web"""
    print("\n" + "="*80)
    print("TEST 4: Data Priority - Should check DB before web search")
    print("="*80)
    
    session_id = "test_session_4"
    question = "Какие продажи в Минске за последний месяц?"
    
    print(f"\nQuestion: {question}")
    print("Expected: AI should query database first (INTERNAL_DB or HYBRID)")
    
    result = await unified_intelligence_service.process_message(session_id, question)
    
    print(f"\n--- CLASSIFICATION ---")
    print(f"Type: {result['classification'].get('type')}")
    
    if result['classification'].get('type') in ['INTERNAL_DB', 'HYBRID']:
        print("✓ SUCCESS: AI correctly prioritized database!")
    else:
        print("✗ WARNING: AI did not prioritize database")
    
    print(f"\n--- SOURCES USED ---")
    for source in result['sources']:
        print(f"- {source['type'].upper()}: {source['status']}")
    
    print(f"\n--- AI RESPONSE ---")
    print(result['response'])
    
    return result


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("AI BRAIN CONFIGURATION - VERIFICATION TESTS")
    print("="*80)
    
    try:
        # Test 1: Strategic Analysis
        await test_strategic_analysis()
        
        # Test 2: Memory Injection
        await test_memory_injection()
        
        # Test 3: Belarus Expertise
        await test_belarus_expertise()
        
        # Test 4: Data Priority
        await test_data_priority()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED")
        print("="*80)
        
        # Show all learned facts
        facts = company_knowledge_service.get_all_facts()
        print(f"\n\nTotal facts in knowledge base: {len(facts)}")
        if facts:
            print("\nLearned facts:")
            for fact in facts:
                print(f"  [{fact['category']}] {fact['fact']}")
        
    except Exception as e:
        print(f"\n\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
