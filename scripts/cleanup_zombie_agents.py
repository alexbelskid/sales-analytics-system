"""
Cleanup Script: Remove "Zombie" Agents
Удаляет агентов без данных (отголоски прошлого)
"""

import requests

API_URL = "http://localhost:8000"

def cleanup_zombie_agents():
    """Remove agents that have no sales data or plans"""
    
    print("🧹 Cleaning up zombie agents (agents without data)...")
    print("="*60)
    
    # Option 1: Delete all agents data (nuclear option)
    print("\nOption 1: DELETE ALL AGENT DATA")
    print("This will delete ALL agents and their data from the database.")
    response = input("Type 'yes' to proceed: ")
    
    if response.lower() == 'yes':
        try:
            result = requests.delete(f"{API_URL}/api/files/delete-all-data")
            result.raise_for_status()
            data = result.json()
            
            if data.get('success'):
                print(f"✅ {data.get('message')}")
                print(f"   {data.get('details')}")
            else:
                print(f"❌ Error: {data.get('message')}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    else:
        print("❌ Cleanup cancelled")

if __name__ == "__main__":
    cleanup_zombie_agents()
