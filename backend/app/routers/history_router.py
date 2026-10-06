from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import DiagnosticSession, Attempt, Question, Concept, Topic

router = APIRouter(prefix="/history", tags=["Learning History & Sessions"])

@router.get("")
async def get_student_history(
    student_id: Optional[str] = Query(default="student_demo_1"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    stmt = (
        select(DiagnosticSession, Topic)
        .join(Topic, DiagnosticSession.topic_id == Topic.id)
        .where(DiagnosticSession.student_id == student_id)
        .order_by(DiagnosticSession.started_at.desc())
    )
    res = await db.execute(stmt)
    sessions = res.all()

    output = []
    for s, topic in sessions:
        # Get attempts count
        att_stmt = select(Attempt).where(Attempt.session_id == s.id)
        att_res = await db.execute(att_stmt)
        attempts = list(att_res.scalars().all())

        total = len(attempts)
        correct = sum(1 for a in attempts if a.is_correct)
        avg_conf = (sum(a.confidence_score for a in attempts) / total) if total > 0 else 0.0

        output.append({
            "session_id": s.id,
            "topic_id": s.topic_id,
            "topic_name": topic.name,
            "status": s.status,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            "total_questions": total,
            "correct_count": correct,
            "accuracy_percentage": round((correct / total * 100.0) if total > 0 else 0.0, 1),
            "avg_confidence": round(avg_conf, 1)
        })

    return output
