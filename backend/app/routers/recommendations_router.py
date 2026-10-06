from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Recommendation, Concept
from app.schemas.schemas import RecommendationResponse
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter(prefix="/recommendations", tags=["Personalized Recommendations"])

@router.get("", response_model=List[RecommendationResponse])
async def list_recommendations(
    student_id: Optional[str] = Query(default="student_demo_1"),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Refresh recommendations dynamically
        await RecommendationEngine.generate_recommendations_for_student(db, student_id)

        stmt = (
            select(Recommendation, Concept)
            .join(Concept, Recommendation.target_concept_id == Concept.id)
            .where(
                Recommendation.student_id == student_id,
                Recommendation.is_completed == False
            )
            .order_by(Recommendation.priority.desc())
        )
        res = await db.execute(stmt)
        rows = res.all()

        output = []
        for rec, target_concept in rows:
            root_name = None
            if rec.root_cause_concept_id:
                r_stmt = select(Concept).where(Concept.id == rec.root_cause_concept_id)
                r_res = await db.execute(r_stmt)
                root_c = r_res.scalar_one_or_none()
                root_name = root_c.name if root_c else None

            action_steps = rec.action_steps if isinstance(rec.action_steps, list) else []

            output.append(RecommendationResponse(
                id=rec.id,
                concept_id=target_concept.id,
                concept_name=target_concept.name,
                root_cause_concept_id=rec.root_cause_concept_id,
                root_cause_concept_name=root_name,
                title=rec.title,
                reason=rec.reason,
                action_steps=action_steps,
                priority=rec.priority,
                is_completed=rec.is_completed
            ))
        return output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{recommendation_id}/complete")
async def mark_complete(recommendation_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Recommendation).where(Recommendation.id == recommendation_id)
    res = await db.execute(stmt)
    rec = res.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.is_completed = True
    await db.flush()
    return {"status": "success", "message": "Recommendation marked as completed"}
