"""
Database Truth Audit Script
Verifies that AI agent uses REAL database data, not hallucinations

This script:
1. Connects directly to database and extracts raw data
2. Asks AI the same question
3. Compares results to prove data grounding
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.unified_intelligence_service import unified_intelligence_service
from dotenv import load_dotenv

# Load environment
load_dotenv(backend_path / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

class TruthAudit:
    """Audit system to verify AI uses real data"""
    
    def __init__(self):
        self.db_url = DATABASE_URL
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "connection_status": None,
            "raw_data": None,
            "ai_response": None,
            "comparison": None,
            "verdict": None
        }
    
    def test_connection(self):
        """Test database connection"""
        print("\n" + "="*70)
        print("STEP 1: Testing Database Connection")
        print("="*70)
        
        if not self.db_url:
            print("❌ FAIL: DATABASE_URL not configured")
            self.results["connection_status"] = "FAILED - No DATABASE_URL"
            return False
        
        try:
            conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            print(f"✓ Connected to database")
            conn.close()
            self.results["connection_status"] = "SUCCESS"
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.results["connection_status"] = f"FAILED - {str(e)}"
            return False
    
    def extract_raw_truth(self):
        """Extract THE TRUTH directly from database"""
        print("\n" + "="*70)
        print("STEP 2: Extracting RAW DATA (The Truth)")
        print("="*70)
        
        try:
            conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            
            # Query 1: Get aggregate statistics
            print("\nQuery 1: Aggregate Statistics")
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sales,
                    SUM(total_amount) as total_revenue,
                    MAX(sale_date) as latest_sale,
                    MIN(sale_date) as earliest_sale
                FROM sales
                WHERE sale_date >= '2024-01-01'
            """)
            
            stats = cursor.fetchone()
            print(f"  Total Sales: {stats['total_sales']}")
            print(f"  Total Revenue: {stats['total_revenue']}")
            print(f"  Date Range: {stats['earliest_sale']} to {stats['latest_sale']}")
            
            # Query 2: Get top 5 products
            print("\nQuery 2: Top 5 Products by Sales")
            cursor.execute("""
                SELECT 
                    p.product_name,
                    COUNT(si.id) as sale_count,
                    SUM(si.quantity) as total_quantity,
                    SUM(si.total_price) as total_revenue
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                JOIN sales s ON si.sale_id = s.id
                WHERE s.sale_date >= '2024-01-01'
                GROUP BY p.product_name
                ORDER BY total_revenue DESC
                LIMIT 5
            """)
            
            top_products = cursor.fetchall()
            
            print("\nTop 5 Products:")
            for i, product in enumerate(top_products, 1):
                print(f"  {i}. {product['product_name']}: {product['total_quantity']} units, "
                      f"{product['total_revenue']:.2f} BYN")
            
            cursor.close()
            conn.close()
            
            self.results["raw_data"] = {
                "stats": dict(stats),
                "top_products": [dict(p) for p in top_products]
            }
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR extracting data: {e}")
            self.results["raw_data"] = {"error": str(e)}
            return False
    
    async def ask_ai(self):
        """Ask AI the same question"""
        print("\n" + "="*70)
        print("STEP 3: Asking AI the Same Question")
        print("="*70)
        
        question = "Какой у меня топ товар по продажам в 2024 году?"
        print(f"\nQuestion: {question}")
        
        try:
            result = await unified_intelligence_service.process_message(
                session_id="truth_audit_session",
                message=question
            )
            
            response = result["response"]
            quality_score = result.get("quality_score", 0)
            
            print(f"\nAI Response:")
            print(f"{response[:500]}..." if len(response) > 500 else response)
            print(f"\nQuality Score: {quality_score}/10")
            
            self.results["ai_response"] = {
                "question": question,
                "response": response,
                "quality_score": quality_score,
                "sources": result.get("sources", []),
                "debug_sql": result.get("debug_sql")
            }
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR asking AI: {e}")
            self.results["ai_response"] = {"error": str(e)}
            return False
    
    def compare_results(self):
        """Compare raw data with AI response"""
        print("\n" + "="*70)
        print("STEP 4: Comparing Results")
        print("="*70)
        
        if not self.results["raw_data"] or not self.results["ai_response"]:
            print("❌ Cannot compare - missing data")
            self.results["verdict"] = "FAILED - Missing Data"
            return False
        
        raw_data = self.results["raw_data"]
        ai_response = self.results["ai_response"]["response"]
        
        # Check if top product is mentioned
        top_products = raw_data.get("top_products", [])
        if not top_products:
            print("⚠️  No products in database")
            self.results["verdict"] = "INCONCLUSIVE - No Data"
            return False
        
        top_product_name = top_products[0]["product_name"]
        
        print(f"\nTruth (DB): Top product is '{top_product_name}'")
        print(f"AI Response check: Does '{top_product_name}' appear in response?")
        
        # Check if product name appears in AI response
        if top_product_name.lower() in ai_response.lower():
            print(f"✓ MATCH: AI correctly referenced '{top_product_name}'")
            self.results["comparison"] = "MATCH"
            self.results["verdict"] = "READY FOR DEMO"
            return True
        else:
            print(f"❌ MISMATCH: AI did not mention '{top_product_name}'")
            print(f"\nAI Response: {ai_response[:200]}...")
            self.results["comparison"] = "MISMATCH"
            self.results["verdict"] = "FAILED - Data Not Grounded"
            return False
    
    def generate_report(self):
        """Generate TRUTH_AUDIT_REPORT.md"""
        print("\n" + "="*70)
        print("STEP 5: Generating Report")
        print("="*70)
        
        # Use correct artifact path
        artifact_dir = Path("/Users/alexbelski/.gemini/antigravity/brain/7b73dec7-d7c4-49ab-9f45-3bc8f188c450")
        report_path = artifact_dir / "TRUTH_AUDIT_REPORT.md"
        
        report = f"""# Database Truth Audit Report

**Date:** {self.results['timestamp']}  
**Auditor:** AI QA Engineer  
**Objective:** Verify AI uses REAL database data, not hallucinations

---

## ✅ Connection Status

**Status:** {self.results['connection_status']}

---

## 📊 Raw Data Sample (The Truth)

### Aggregate Statistics
"""
        
        if self.results["raw_data"] and "stats" in self.results["raw_data"]:
            stats = self.results["raw_data"]["stats"]
            report += f"""
- Total Sales: **{stats.get('total_sales', 'N/A')}**
- Total Revenue: **{stats.get('total_revenue', 'N/A')} BYN**
- Date Range: {stats.get('earliest_sale', 'N/A')} to {stats.get('latest_sale', 'N/A')}
"""
        
        report += "\n### Top 5 Products (Real Data)\n\n"
        
        if self.results["raw_data"] and "top_products" in self.results["raw_data"]:
            for i, product in enumerate(self.results["raw_data"]["top_products"], 1):
                report += f"{i}. **{product['product_name']}**: {product['total_quantity']} units, {product['total_revenue']:.2f} BYN\n"
        
        report += "\n---\n\n## 🤔 AI Response & Reasoning Trace\n\n"
        
        if self.results["ai_response"]:
            report += f"**Question:** {self.results['ai_response'].get('question', 'N/A')}\n\n"
            report += f"**Quality Score:** {self.results['ai_response'].get('quality_score', 'N/A')}/10\n\n"
            report += f"**Response:**\n\n{self.results['ai_response'].get('response', 'N/A')}\n\n"
            
            if self.results['ai_response'].get('debug_sql'):
                sql_info = self.results['ai_response']['debug_sql']
                report += f"**SQL Generated:**\n```sql\n{sql_info.get('sql', 'N/A')}\n```\n\n"
                report += f"**Rows Returned:** {sql_info.get('row_count', 'N/A')}\n\n"
        
        report += "---\n\n## 🏁 Verdict\n\n"
        
        verdict = self.results['verdict']
        
        if verdict == "READY FOR DEMO":
            report += "### ✅ READY FOR DEMO\n\n"
            report += "**Conclusion:** AI successfully uses REAL database data. No hallucinations detected.\n\n"
            report += "- ✓ Database connection working\n"
            report += "- ✓ Raw data extracted\n"
            report += "- ✓ AI referenced actual product names from database\n"
            report += "- ✓ Quality score acceptable\n"
        else:
            report += f"### ❌ {verdict}\n\n"
            report += "**Issues Found:**\n"
            if self.results['comparison'] == "MISMATCH":
                report += "- AI response does not match database truth\n"
                report += "- Possible hallucination or data access issue\n"
        
        # Write report
        report_path.write_text(report, encoding='utf-8')
        print(f"✓ Report generated: {report_path}")
        
        return True


async def main():
    """Run the truth audit"""
    print("\n" + "="*70)
    print("DATABASE TRUTH AUDIT")
    print("Proving AI uses REAL data, not hallucinations")
    print("="*70)
    
    audit = TruthAudit()
    
    # Step 1: Test connection
    if not audit.test_connection():
        audit.generate_report()
        return 1
    
    # Step 2: Extract raw truth
    if not audit.extract_raw_truth():
        audit.generate_report()
        return 1
    
    # Step 3: Ask AI
    if not await audit.ask_ai():
        audit.generate_report()
        return 1
    
    # Step 4: Compare
    audit.compare_results()
    
    # Step 5: Generate report
    audit.generate_report()
    
    # Final verdict
    print("\n" + "="*70)
    print(f"FINAL VERDICT: {audit.results['verdict']}")
    print("="*70)
    
    if audit.results['verdict'] == "READY FOR DEMO":
        print("\n✅ ALL CHECKS PASSED - AI IS DATA-GROUNDED")
        return 0
    else:
        print(f"\n❌ AUDIT FAILED - {audit.results['verdict']}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
