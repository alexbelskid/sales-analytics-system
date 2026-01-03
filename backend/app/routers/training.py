"""
Training Examples Router
CRUD operations for AI training examples (question-answer pairs)
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging
import csv
import io

from app.database import get_supabase

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


@router.get("", response_model=List[TrainingExample])
async def list_training_examples(tone: Optional[str] = None, limit: int = 100):
    """
    List training examples, optionally filtered by tone
    
    Args:
        tone: Filter by tone
        limit: Maximum number of examples to return
    """
    try:
        supabase = get_supabase()
        
        query = supabase.table("training_examples").select("*")
        
        if tone:
            query = query.eq("tone", tone)
        
        response = query.order("confidence_score", desc=True).limit(limit).execute()
        
        return response.data
        
    except Exception as e:
        logger.error(f"Error listing training examples: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{example_id}", response_model=TrainingExample)
async def get_training_example(example_id: str):
    """Get single training example by ID"""
    try:
        supabase = get_supabase()
        
        response = supabase.table("training_examples").select("*").eq("id", example_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Training example not found")
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting training example: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=TrainingExample)
async def create_training_example(example: TrainingCreate):
    """Create new training example"""
    try:
        supabase = get_supabase()
        
        data = {
            "question": example.question,
            "answer": example.answer,
            "tone": example.tone,
            "confidence_score": example.confidence_score
        }
        
        response = supabase.table("training_examples").insert(data).execute()
        
        return response.data[0]
        
    except Exception as e:
        logger.error(f"Error creating training example: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{example_id}", response_model=TrainingExample)
async def update_training_example(example_id: str, example: TrainingUpdate):
    """Update existing training example"""
    try:
        supabase = get_supabase()
        
        # Build update data
        update_data = {}
        if example.question is not None:
            update_data["question"] = example.question
        if example.answer is not None:
            update_data["answer"] = example.answer
        if example.tone is not None:
            update_data["tone"] = example.tone
        if example.confidence_score is not None:
            update_data["confidence_score"] = example.confidence_score
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase.table("training_examples").update(update_data).eq("id", example_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Training example not found")
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating training example: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{example_id}")
async def delete_training_example(example_id: str):
    """Delete training example"""
    try:
        supabase = get_supabase()
        
        response = supabase.table("training_examples").delete().eq("id", example_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Training example not found")
        
        return {"success": True, "message": "Training example deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting training example: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/csv")
async def upload_csv_examples(file: UploadFile = File(...)):
    """
    Upload training examples from CSV file
    
    CSV format: question,answer,tone
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be CSV format")
        
        # Read CSV
        contents = await file.read()
        csv_data = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        # Validate headers
        required_headers = {'question', 'answer'}
        if not required_headers.issubset(set(csv_reader.fieldnames or [])):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must have columns: {', '.join(required_headers)}"
            )
        
        # Parse and insert
        supabase = get_supabase()
        examples = []
        
        for row in csv_reader:
            example = {
                "question": row["question"],
                "answer": row["answer"],
                "tone": row.get("tone", "professional"),
                "confidence_score": float(row.get("confidence_score", 1.0))
            }
            examples.append(example)
        
        if not examples:
            raise HTTPException(status_code=400, detail="No valid examples found in CSV")
        
        response = supabase.table("training_examples").insert(examples).execute()
        
        return {
            "success": True,
            "message": f"Uploaded {len(examples)} training examples",
            "count": len(examples)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_training_stats():
    """Get training examples statistics"""
    try:
        supabase = get_supabase()
        
        response = supabase.table("training_examples").select("tone, confidence_score").execute()
        
        # Count by tone
        tones = {}
        total_confidence = 0
        
        for item in response.data:
            tone = item["tone"]
            tones[tone] = tones.get(tone, 0) + 1
            total_confidence += item.get("confidence_score", 1.0)
        
        avg_confidence = total_confidence / len(response.data) if response.data else 0
        
        return {
            "total": len(response.data),
            "by_tone": tones,
            "average_confidence": round(avg_confidence, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting training stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
