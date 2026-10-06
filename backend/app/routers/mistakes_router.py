from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.schemas import MistakeResponse
from app.services.mistake_analyzer import MistakeAnalyzer

router = APIRouter(prefix="/mistakes", tags=["Mistake Analyzer"])

@router.get("", response_model=List[MistakeResponse])
async def list_mistakes(
    student_id: Optional[str] = Query(default="student_demo_1"),
    db: AsyncSession = Depends(get_db)
):
    try:
        mistakes = await MistakeAnalyzer.get_student_mistake_history(db, student_id)
        return [MistakeResponse(**m) for m in mistakes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
