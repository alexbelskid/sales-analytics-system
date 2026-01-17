"""
Company Knowledge Service
Manages dynamic company facts and Belarus market context
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

# Path to knowledge base
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"
COMPANY_CONTEXT_FILE = KNOWLEDGE_DIR / "company_context.json"

# Thread lock for file operations
_file_lock = threading.Lock()


class CompanyKnowledgeService:
    """
    Service for managing company-specific knowledge and Belarus market context.
    Provides persistent storage for user-taught facts.
    """
    
    def __init__(self):
        self._ensure_knowledge_dir()
        self._context_cache: Optional[Dict] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl_seconds = 300  # 5 minutes
    
    def _ensure_knowledge_dir(self):
        """Ensure knowledge directory and files exist"""
        try:
            KNOWLEDGE_DIR.mkdir(exist_ok=True)
            
            if not COMPANY_CONTEXT_FILE.exists():
                # Create default context
                default_context = {
                    "facts": [],
                    "belarus_context": {
                        "regions": [
                            "Минская область",
                            "Брестская область",
                            "Гродненская область",
                            "Гомельская область",
                            "Могилевская область",
                            "Витебская область"
                        ],
                        "major_cities": [
                            "Минск", "Гомель", "Могилев", 
                            "Витебск", "Гродно", "Брест"
                        ],
                        "tax_rate_vat": 20,
                        "currency": "BYN",
                        "logistics_notes": "Основные транспортные коридоры: М1 (Брест-Минск-граница РФ), М5 (Минск-Гомель), М6 (Минск-Гродно)",
                        "retail_specifics": "Основные форматы: гипермаркеты (Евроопт, Корона), региональные сети, частные магазины"
                    },
                    "metadata": {
                        "version": "1.0",
                        "last_updated": datetime.now().isoformat(),
                        "description": "Dynamic company knowledge base for AI context"
                    }
                }
                self._save_context(default_context)
        except Exception as e:
            logger.error(f"Failed to initialize knowledge directory: {e}")
    
    def _load_context(self) -> Dict[str, Any]:
        """Load company context from JSON file with caching"""
        # Check cache
        if self._context_cache and self._cache_timestamp:
            age = (datetime.now() - self._cache_timestamp).total_seconds()
            if age < self._cache_ttl_seconds:
                return self._context_cache
        
        # Load from file
        try:
            with _file_lock:
                if COMPANY_CONTEXT_FILE.exists():
                    with open(COMPANY_CONTEXT_FILE, 'r', encoding='utf-8') as f:
                        try:
                            context = json.load(f)
                            # Validate structure
                            if not isinstance(context, dict):
                                raise ValueError("Context is not a dictionary")
                            if "facts" not in context or not isinstance(context["facts"], list):
                                logger.warning("Invalid facts structure, resetting")
                                context["facts"] = []
                            if "belarus_context" not in context or not isinstance(context["belarus_context"], dict):
                                logger.warning("Invalid belarus_context structure, resetting")
                                context["belarus_context"] = {}
                            
                            self._context_cache = context
                            self._cache_timestamp = datetime.now()
                            return context
                        except json.JSONDecodeError as e:
                            logger.error(f"Corrupted JSON in company_context.json: {e}")
                            logger.info("Creating backup and reinitializing...")
                            # Backup corrupted file
                            backup_path = COMPANY_CONTEXT_FILE.with_suffix('.json.corrupted')
                            COMPANY_CONTEXT_FILE.rename(backup_path)
                            # Reinitialize
                            self._ensure_knowledge_dir()
                            return self._load_context()
        except Exception as e:
            logger.error(f"Failed to load company context: {e}")
        
        return {"facts": [], "belarus_context": {}, "metadata": {}}
    
    def _save_context(self, context: Dict[str, Any]):
        """Save company context to JSON file"""
        try:
            with _file_lock:
                # Update metadata
                if "metadata" not in context:
                    context["metadata"] = {}
                context["metadata"]["last_updated"] = datetime.now().isoformat()
                
                # Write to file
                with open(COMPANY_CONTEXT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(context, f, ensure_ascii=False, indent=2)
                
                # Invalidate cache
                self._context_cache = context
                self._cache_timestamp = datetime.now()
                
                logger.info(f"Company context saved: {len(context.get('facts', []))} facts")
        except Exception as e:
            logger.error(f"Failed to save company context: {e}")
            raise
    
    def get_belarus_context(self) -> Dict[str, Any]:
        """Get Belarus market context"""
        context = self._load_context()
        return context.get("belarus_context", {})
    
    def get_all_facts(self) -> List[Dict[str, Any]]:
        """Get all company facts"""
        context = self._load_context()
        return context.get("facts", [])
    
    def get_facts_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get facts filtered by category"""
        facts = self.get_all_facts()
        return [f for f in facts if f.get("category") == category]
    
    def add_fact(
        self, 
        fact: str, 
        category: str = "other",
        created_by: str = "user",
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """
        Add a new fact to the knowledge base
        
        Args:
            fact: The fact text (e.g., "В Гродно у нас теперь новый склад")
            category: Category (logistics, products, regions, partners, other)
            created_by: Who created this fact (user, system)
            confidence: Confidence score 0.0-1.0
            
        Returns:
            The created fact object
        """
        # Validate inputs
        if not fact or not fact.strip():
            raise ValueError("Fact cannot be empty")
        
        if len(fact) > 1000:
            raise ValueError("Fact is too long (max 1000 characters)")
        
        valid_categories = ["logistics", "products", "regions", "partners", "other"]
        if category not in valid_categories:
            logger.warning(f"Invalid category '{category}', using 'other'")
            category = "other"
        
        if not (0.0 <= confidence <= 1.0):
            logger.warning(f"Invalid confidence {confidence}, using 1.0")
            confidence = 1.0
        
        context = self._load_context()
        
        new_fact = {
            "id": str(uuid.uuid4()),
            "category": category,
            "fact": fact.strip(),
            "created_at": datetime.now().isoformat(),
            "created_by": created_by,
            "confidence": confidence
        }
        
        if "facts" not in context:
            context["facts"] = []
        
        context["facts"].append(new_fact)
        self._save_context(context)
        
        logger.info(f"Added new fact: {fact[:50]}...")
        return new_fact
    
    def remove_fact(self, fact_id: str) -> bool:
        """Remove a fact by ID"""
        context = self._load_context()
        facts = context.get("facts", [])
        
        original_count = len(facts)
        context["facts"] = [f for f in facts if f.get("id") != fact_id]
        
        if len(context["facts"]) < original_count:
            self._save_context(context)
            logger.info(f"Removed fact: {fact_id}")
            return True
        
        return False
    
    def get_context_for_ai(self) -> str:
        """
        Get formatted context string for AI prompts
        
        Returns:
            Formatted string with Belarus context and company facts
        """
        context = self._load_context()
        belarus = context.get("belarus_context", {})
        facts = context.get("facts", [])
        
        lines = []
        
        # Belarus Market Context
        lines.append("=== КОНТЕКСТ РЫНКА БЕЛАРУСИ ===")
        if belarus.get("regions"):
            lines.append(f"Регионы: {', '.join(belarus['regions'])}")
        if belarus.get("major_cities"):
            lines.append(f"Крупные города: {', '.join(belarus['major_cities'])}")
        if belarus.get("currency"):
            lines.append(f"Валюта: {belarus['currency']}")
        if belarus.get("tax_rate_vat"):
            lines.append(f"НДС: {belarus['tax_rate_vat']}%")
        if belarus.get("logistics_notes"):
            lines.append(f"Логистика: {belarus['logistics_notes']}")
        if belarus.get("retail_specifics"):
            lines.append(f"Ритейл: {belarus['retail_specifics']}")
        
        # Company Facts
        if facts:
            lines.append("\n=== ФАКТЫ О КОМПАНИИ ===")
            for fact in facts[-10:]:  # Last 10 facts
                category = fact.get("category", "other")
                fact_text = fact.get("fact", "")
                lines.append(f"[{category.upper()}] {fact_text}")
        
        return "\n".join(lines)
    
    def search_facts(self, query: str) -> List[Dict[str, Any]]:
        """
        Search facts by text query
        
        Args:
            query: Search query (case-insensitive)
            
        Returns:
            List of matching facts
        """
        facts = self.get_all_facts()
        query_lower = query.lower()
        
        return [
            f for f in facts 
            if query_lower in f.get("fact", "").lower()
        ]


# Global singleton
company_knowledge_service = CompanyKnowledgeService()
