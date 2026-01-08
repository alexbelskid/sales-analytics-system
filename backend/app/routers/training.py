"""
Training Examples Router
CRUD operations for AI training examples
Uses direct PostgreSQL connection to bypass PostgREST schema cache issues
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging
import csv
import io

from app import db_direct

logger = logging.getLogger(__name__)

router = APIRouter()


class TrainingExample(BaseModel):
    """Training example model"""
    id: Optional[str] = None
    question: str
    answer: str
    tone: str = "professional"
    confidence_score: float = 1.0
    created_at: Optional[datetime] = None


class TrainingCreate(BaseModel):
    """Create training example"""
    question: str
    answer: str
    tone: str = "professional"
    confidence_score: float = 1.0


class TrainingUpdate(BaseModel):
    """Update training example"""
    question: Optional[str] = None
    answer: Optional[str] = None
    tone: Optional[str] = None
    confidence_score: Optional[float] = None


VALID_TONES = ["professional", "friendly", "formal", "brief", "detailed", "creative"]


@router.get("", response_model=List[TrainingExample])
async def list_training(tone: Optional[str] = None):
    """List all training examples"""
    try:
        items = db_direct.get_all_training(tone)
        return items
    except Exception as e:
        logger.error(f"Error listing training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=TrainingExample)
async def create_training(item: TrainingCreate):
    """Create new training example"""
    try:
        if item.tone not in VALID_TONES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid tone. Must be one of: {', '.join(VALID_TONES)}"
            )
        
        result = db_direct.insert_training(
            item.question, 
            item.answer, 
            item.tone, 
            item.confidence_score
        )
        logger.info(f"Created training example: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{item_id}")
async def delete_training(item_id: str):
    """Delete training example"""
    try:
        success = db_direct.delete_training(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Training example not found")
        return {"success": True, "message": "Training example deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/csv")
async def upload_training_csv(file: UploadFile = File(...)):
    """Upload training examples from CSV file"""
    try:
        content = await file.read()
        text = content.decode('utf-8')
        
        reader = csv.DictReader(io.StringIO(text))
        created = 0
        
        for row in reader:
            question = row.get('question', row.get('вопрос', ''))
            answer = row.get('answer', row.get('ответ', ''))
            tone = row.get('tone', row.get('тон', 'professional'))
            
            if question and answer:
                if tone not in VALID_TONES:
                    tone = 'professional'
                db_direct.insert_training(question, answer, tone, 1.0)
                created += 1
        
        return {"success": True, "created": created}
        
    except Exception as e:
        logger.error(f"Error uploading training CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))
