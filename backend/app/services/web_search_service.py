"""
Web Search Service - External Market Intelligence
Integrates Tavily API for gathering external data: news, market trends, regulations
"""

from typing import List, Dict, Optional
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class WebSearchService:
    """Service for searching external web data using Tavily API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'tavily_api_key', '')
        self.base_url = "https://api.tavily.com"
        self.max_results = getattr(settings, 'web_search_max_results', 5)
        
    def is_available(self) -> bool:
        """Check if web search is configured"""
        return bool(self.api_key)
    
    async def search(
        self,
        query: str,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        max_results: Optional[int] = None
    ) -> Dict:
        """
        Search the web using Tavily API
        
        Args:
            query: Search query in natural language
            search_depth: "basic" or "advanced" (advanced is more thorough but slower)
            include_domains: Optional list of domains to prioritize
            exclude_domains: Optional list of domains to exclude
            max_results: Maximum number of results (default from config)
            
        Returns:
            {
                "success": bool,
                "results": [{"title": str, "url": str, "content": str, "score": float}],
                "summary": str,
                "query": str,
                "error": Optional[str]
            }
        """
        if not self.is_available():
            return {
                "success": False,
                "results": [],
                "summary": "",
                "query": query,
                "error": "Tavily API key not configured. Add TAVILY_API_KEY to .env"
            }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "api_key": self.api_key,
                    "query": query,
                    "search_depth": search_depth,
                    "max_results": max_results or self.max_results,
                    "include_answer": True,  # Get AI-generated summary
                    "include_raw_content": False,  # Don't need full HTML
                }
                
                if include_domains:
                    payload["include_domains"] = include_domains
                if exclude_domains:
                    payload["exclude_domains"] = exclude_domains
                
                response = await client.post(
                    f"{self.base_url}/search",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                # Format results
                results = []
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                        "score": item.get("score", 0.0)
                    })
                
                return {
                    "success": True,
                    "results": results,
                    "summary": data.get("answer", ""),
                    "query": query,
                    "error": None
                }
                
        except httpx.HTTPError as e:
            logger.error(f"Tavily API HTTP error: {e}")
            return {
                "success": False,
                "results": [],
                "summary": "",
                "query": query,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Tavily API error: {e}")
            return {
                "success": False,
                "results": [],
                "summary": "",
                "query": query,
                "error": str(e)
            }
    
    async def search_news(self, topic: str, region: str = "Belarus") -> Dict:
        """
        Search for recent news about a topic
        
        Args:
            topic: News topic (e.g., "dairy market", "inflation")
            region: Region to focus on (default: Belarus)
            
        Returns:
            Search results focused on news
        """
        query = f"{topic} {region} news последние новости"
        
        # Prioritize news domains
        news_domains = [
            "belta.by", "naviny.by", "ont.by",  # Belarus news
            "interfax.ru", "tass.ru",  # Russian news
            "reuters.com", "bloomberg.com"  # International
        ]
        
        return await self.search(
            query=query,
            search_depth="basic",
            include_domains=news_domains,
            max_results=5
        )
    
    async def search_market_data(self, query: str) -> Dict:
        """
        Search for market data, trends, statistics
        
        Args:
            query: Market data query (e.g., "inflation rate Belarus 2025")
            
        Returns:
            Search results focused on data sources
        """
        # Prioritize data/statistics sources
        data_domains = [
            "belstat.gov.by",  # Belarus statistics
            "nbrb.by",  # National Bank of Belarus
            "worldbank.org", "imf.org",  # International data
            "tradingeconomics.com"
        ]
        
        return await self.search(
            query=query,
            search_depth="advanced",  # More thorough for data
            include_domains=data_domains,
            max_results=5
        )
    
    async def get_status(self) -> Dict:
        """Get service status"""
        return {
            "service": "web_search",
            "provider": "tavily",
            "available": self.is_available(),
            "configured": bool(self.api_key),
            "max_results": self.max_results
        }


# Global instance
web_search_service = WebSearchService()
