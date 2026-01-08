"""
Direct PostgreSQL Database Connection
Uses psycopg2 for operations that don't work well with PostgREST schema cache
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
import logging
from contextlib import contextmanager
from app.config import settings

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """Get a direct PostgreSQL connection"""
    conn = None
    try:
        database_url = settings.database_url
        if not database_url:
            logger.error("DATABASE_URL not configured")
            raise Exception("DATABASE_URL not configured. Please add it to environment variables.")
        
        conn = psycopg2.connect(database_url)
        yield conn
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise Exception(f"Cannot connect to database: {e}")
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


def execute_query(sql: str, params: tuple = None, fetch: bool = True) -> Optional[List[Dict]]:
    """Execute a SQL query and return results"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            if fetch:
                return [dict(row) for row in cur.fetchall()]
            conn.commit()
            return None


def insert_knowledge(category: str, title: str, content: str) -> Dict[str, Any]:
    """Insert a new knowledge base item"""
    sql = """
        INSERT INTO knowledge_base (category, title, content)
        VALUES (%s, %s, %s)
        RETURNING id, category, title, content, created_at, updated_at
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (category, title, content))
            result = dict(cur.fetchone())
            conn.commit()
            return result


def get_all_knowledge(category: str = None) -> List[Dict[str, Any]]:
    """Get all knowledge items, optionally filtered by category"""
    if category:
        sql = "SELECT * FROM knowledge_base WHERE category = %s ORDER BY created_at DESC"
        params = (category,)
    else:
        sql = "SELECT * FROM knowledge_base ORDER BY created_at DESC"
        params = None
    
    return execute_query(sql, params) or []


def get_knowledge_by_id(item_id: str) -> Optional[Dict[str, Any]]:
    """Get a single knowledge item by ID"""
    sql = "SELECT * FROM knowledge_base WHERE id = %s"
    result = execute_query(sql, (item_id,))
    return result[0] if result else None


def update_knowledge(item_id: str, category: str = None, title: str = None, content: str = None) -> Optional[Dict[str, Any]]:
    """Update a knowledge item"""
    updates = []
    params = []
    
    if category:
        updates.append("category = %s")
        params.append(category)
    if title:
        updates.append("title = %s")
        params.append(title)
    if content:
        updates.append("content = %s")
        params.append(content)
    
    if not updates:
        return None
    
    updates.append("updated_at = NOW()")
    params.append(item_id)
    
    sql = f"UPDATE knowledge_base SET {', '.join(updates)} WHERE id = %s RETURNING *"
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, tuple(params))
            result = cur.fetchone()
            conn.commit()
            return dict(result) if result else None


def delete_knowledge(item_id: str) -> bool:
    """Delete a knowledge item"""
    sql = "DELETE FROM knowledge_base WHERE id = %s RETURNING id"
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (item_id,))
            result = cur.fetchone()
            conn.commit()
            return result is not None


# Training examples functions
def insert_training(question: str, answer: str, tone: str = "professional", confidence_score: float = 1.0) -> Dict[str, Any]:
    """Insert a new training example"""
    sql = """
        INSERT INTO training_examples (question, answer, tone, confidence_score)
        VALUES (%s, %s, %s, %s)
        RETURNING id, question, answer, tone, confidence_score, created_at
    """
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (question, answer, tone, confidence_score))
            result = dict(cur.fetchone())
            conn.commit()
            return result


def get_all_training(tone: str = None) -> List[Dict[str, Any]]:
    """Get all training examples"""
    if tone:
        sql = "SELECT * FROM training_examples WHERE tone = %s ORDER BY created_at DESC"
        params = (tone,)
    else:
        sql = "SELECT * FROM training_examples ORDER BY created_at DESC"
        params = None
    
    return execute_query(sql, params) or []


def update_training(item_id: str, question: str = None, answer: str = None, tone: str = None, confidence_score: float = None) -> Optional[Dict[str, Any]]:
    """Update a training example"""
    updates = []
    params = []
    
    if question:
        updates.append("question = %s")
        params.append(question)
    if answer:
        updates.append("answer = %s")
        params.append(answer)
    if tone:
        updates.append("tone = %s")
        params.append(tone)
    if confidence_score is not None:
        updates.append("confidence_score = %s")
        params.append(confidence_score)
    
    if not updates:
        return None
    
    params.append(item_id)
    sql = f"UPDATE training_examples SET {', '.join(updates)} WHERE id = %s RETURNING *"
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, tuple(params))
            result = cur.fetchone()
            conn.commit()
            return dict(result) if result else None


def delete_training(item_id: str) -> bool:
    """Delete a training example"""
    sql = "DELETE FROM training_examples WHERE id = %s RETURNING id"
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (item_id,))
            result = cur.fetchone()
            conn.commit()
            return result is not None
