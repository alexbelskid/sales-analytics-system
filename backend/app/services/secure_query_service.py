"""
Secure Query Service - SQL Execution Firewall
Prevents dangerous SQL operations from being executed
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
import psycopg2
from psycopg2 import sql as psycopg_sql
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

from app.config import settings

logger = logging.getLogger(__name__)


class SecurityViolationError(Exception):
    """Raised when a query contains dangerous SQL"""
    pass


class SecureQueryService:
    """
    Secure SQL execution service that acts as a firewall.
    Only allows SELECT and EXPLAIN queries.
    Blocks all DDL and DML operations.
    """
    
    # Dangerous keywords that are NEVER allowed
    BLOCKED_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'INSERT', 'UPDATE', 'ALTER',
        'GRANT', 'REVOKE', 'CREATE', 'REPLACE', 'EXEC', 'EXECUTE',
        'MERGE', 'CALL', 'DO', 'LOCK', 'UNLOCK', 'COPY',
        'VACUUM', 'CLUSTER', 'REINDEX', 'REFRESH', 'COMMENT', 'SECURITY'
    ]
    
    # Only these operations are allowed
    ALLOWED_OPERATIONS = ['SELECT', 'EXPLAIN']
    
    # Maximum query length to prevent abuse
    MAX_QUERY_LENGTH = 10000
    
    # Maximum execution time (seconds)
    QUERY_TIMEOUT = 30
    
    # Maximum rows to return
    MAX_ROWS = 10000
    
    def __init__(self):
        self.database_url = settings.database_url
        if not self.database_url:
            logger.warning("DATABASE_URL not configured - secure queries disabled")
    
    def _get_connection(self, read_only: bool = True):
        """
        Get a database connection with optional READ ONLY mode.
        
        Args:
            read_only: If True, sets transaction to READ ONLY
        """
        if not self.database_url:
            raise ConnectionError("DATABASE_URL not configured")
        
        conn = psycopg2.connect(
            self.database_url,
            cursor_factory=RealDictCursor,
            connect_timeout=10
        )
        conn.set_session(readonly=read_only, autocommit=False)
        
        return conn
    
    @contextmanager
    def _safe_connection(self):
        """Context manager for safe, read-only database connections"""
        conn = None
        try:
            conn = self._get_connection(read_only=True)
            
            # Set statement timeout for this session
            with conn.cursor() as cur:
                cur.execute(f"SET statement_timeout = '{self.QUERY_TIMEOUT * 1000}ms'")
            
            yield conn
            conn.rollback()  # Always rollback - we only read
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a SQL query for security.
        
        Args:
            query: SQL query string
            
        Returns:
            (is_valid, error_message)
        """
        if not query:
            return False, "Empty query"
        
        if len(query) > self.MAX_QUERY_LENGTH:
            return False, f"Query exceeds maximum length ({self.MAX_QUERY_LENGTH} chars)"
        
        # Normalize query for checking
        query_upper = query.upper().strip()
        
        # Remove comments (could be used to hide malicious code)
        query_clean = re.sub(r'--.*$', '', query_upper, flags=re.MULTILINE)
        query_clean = re.sub(r'/\*.*?\*/', '', query_clean, flags=re.DOTALL)
        query_clean = query_clean.strip()
        
        # Check if query starts with allowed operation
        starts_with_allowed = False
        for op in self.ALLOWED_OPERATIONS:
            if query_clean.startswith(op):
                starts_with_allowed = True
                break
        
        if not starts_with_allowed:
            return False, f"Query must start with one of: {', '.join(self.ALLOWED_OPERATIONS)}"
        
        # Check for blocked keywords (word boundaries to avoid false positives)
        for keyword in self.BLOCKED_KEYWORDS:
            # Use word boundary regex to match whole words only
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, query_clean):
                return False, f"Security violation: '{keyword}' operation not allowed"
        
        # Check for multiple statements (semicolon not at the end)
        semicolons = [m.start() for m in re.finditer(r';', query_clean)]
        if len(semicolons) > 1:
            return False, "Multiple statements not allowed"
        if len(semicolons) == 1 and semicolons[0] != len(query_clean) - 1:
            return False, "Multiple statements not allowed"
        
        # Block system tables access
        system_patterns = [
            r'\bPG_CATALOG\b',
            r'\bINFORMATION_SCHEMA\b',
            r'\bPG_PROC\b',
            r'\bPG_ROLES\b',
            r'\bPG_SHADOW\b',
            r'\bPG_AUTHID\b',
        ]
        for pattern in system_patterns:
            if re.search(pattern, query_clean):
                return False, "Access to system tables not allowed"
        
        # Block stored procedure/function calls
        if re.search(r'\bCALL\s+', query_clean) or re.search(r';\s*SELECT', query_clean):
            return False, "Procedure calls not allowed"
        
        return True, None
    
    def execute_safe_query(
        self, 
        query: str, 
        params: Optional[List[Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a SQL query with strict security validation.
        
        Args:
            query: SQL query (must be SELECT or EXPLAIN)
            params: Optional query parameters for safe interpolation
            
        Returns:
            {
                "success": bool,
                "data": List[Dict],
                "row_count": int,
                "columns": List[str],
                "error": Optional[str]
            }
            
        Raises:
            SecurityViolationError: If query contains dangerous operations
        """
        # Step 1: Validate query
        is_valid, error = self.validate_query(query)
        if not is_valid:
            logger.warning(f"Query blocked: {error}. Query: {query[:200]}")
            raise SecurityViolationError(f"Security Violation: {error}")
        
        # Step 2: Execute in read-only transaction
        try:
            with self._safe_connection() as conn:
                with conn.cursor() as cursor:
                    # Execute with parameters if provided
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    # Fetch results with limit
                    rows = cursor.fetchmany(self.MAX_ROWS)
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    
                    # Check if there are more rows (warn if truncated)
                    if cursor.rowcount > self.MAX_ROWS:
                        logger.warning(f"Query results truncated: {cursor.rowcount} rows, returning {self.MAX_ROWS}")
                    
                    return {
                        "success": True,
                        "data": [dict(row) for row in rows],
                        "row_count": len(rows),
                        "columns": columns,
                        "truncated": cursor.rowcount > self.MAX_ROWS if cursor.rowcount >= 0 else False,
                        "error": None
                    }
                    
        except SecurityViolationError:
            raise
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "columns": [],
                "error": f"Database error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return {
                "success": False,
                "data": [],
                "row_count": 0,
                "columns": [],
                "error": str(e)
            }
    
    def is_available(self) -> bool:
        """Check if secure query service is available"""
        if not self.database_url:
            return False
        
        try:
            with self._safe_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Global singleton
secure_query_service = SecureQueryService()
