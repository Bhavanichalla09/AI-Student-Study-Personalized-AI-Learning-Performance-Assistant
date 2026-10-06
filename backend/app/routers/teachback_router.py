from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Concept, TeachBackAttempt, Attempt
from app.schemas.schemas import TeachBackSubmitRequest, TeachBackResponse
from app.services.teachback_evaluator import TeachBackEvaluator
from app.services.mastery_service import MasteryService

router = APIRouter(prefix="/teachback", tags=["Teach-Back Evaluation"])

@router.post("/evaluate", response_model=TeachBackResponse)
async def evaluate_teachback(
    payload: TeachBackSubmitRequest,
    db: AsyncSession = Depends(get_db)
):
    student_id = payload.student_id or "student_demo_1"

    # Fetch concept details
    c_stmt = select(Concept).where(Concept.id == payload.concept_id)
    c_res = await db.execute(c_stmt)
    concept = c_res.scalar_one_or_none()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    # Fetch student's recent quiz accuracy for comparison
    stmt_att = select(Attempt).where(
        Attempt.student_id == student_id,
        Attempt.concept_id == payload.concept_id
    )
    att_res = await db.execute(stmt_att)
    attempts = list(att_res.scalars().all())
    accuracy = (sum(1 for a in attempts if a.is_correct) / len(attempts) * 100.0) if attempts else 50.0

    eval_data = await TeachBackEvaluator.evaluate_explanation(
        concept_name=concept.name,
        concept_code=concept.code,
        student_explanation=payload.student_explanation,
        quiz_accuracy=accuracy
    )

    # Persist TeachBackAttempt
    tb_record = TeachBackAttempt(
        student_id=student_id,
        concept_id=payload.concept_id,
        prompt_text=f"Explain in your own words the mechanics of {concept.name}.",
        student_response=payload.student_explanation,
        accuracy_score=eval_data["accuracy"],
        completeness_score=eval_data["completeness"],
        concept_coverage_score=eval_data["concept_coverage"],
        misconception_detected=eval_data["misconception_detected"],
        misconception_details=eval_data["misconception_details"],
        example_score=eval_data["example_score"],
        overall_score=eval_data["overall_score"],
        feedback=eval_data["feedback"]
    )
    db.add(tb_record)
    await db.flush()

    # Recalculate concept mastery now that teach-back has been provided
    await MasteryService.update_concept_mastery(db, student_id, payload.concept_id)

    return TeachBackResponse(
        id=tb_record.id,
        concept_id=payload.concept_id,
        accuracy=eval_data["accuracy"],
        completeness=eval_data["completeness"],
        concept_coverage=eval_data["concept_coverage"],
        misconception_detected=eval_data["misconception_detected"],
        misconception_details=eval_data["misconception_details"],
        example_score=eval_data["example_score"],
        overall_score=eval_data["overall_score"],
        feedback=eval_data["feedback"],
        quiz_vs_teachback_insight=eval_data["quiz_vs_teachback_insight"]
    )

@router.get("/history/{concept_id}", response_model=List[TeachBackResponse])
async def get_teachback_history(
    concept_id: str,
    student_id: Optional[str] = Query(default="student_demo_1"),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(TeachBackAttempt)
        .where(
            TeachBackAttempt.student_id == student_id,
            TeachBackAttempt.concept_id == concept_id
        )
        .order_by(TeachBackAttempt.created_at.desc())
    )
    res = await db.execute(stmt)
    records = res.scalars().all()

    return [
        TeachBackResponse(
            id=r.id,
            concept_id=r.concept_id,
            accuracy=r.accuracy_score,
            completeness=r.completeness_score,
            concept_coverage=r.concept_coverage_score,
            misconception_detected=r.misconception_detected,
            misconception_details=r.misconception_details,
            example_score=r.example_score,
            overall_score=r.overall_score,
            feedback=r.feedback or "",
            quiz_vs_teachback_insight="Historical record"
        )
        for r in records
    ]
