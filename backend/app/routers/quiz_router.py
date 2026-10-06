from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Concept, Question, DiagnosticSession
from app.schemas.schemas import (
    QuizStartRequest, QuizStartResponse, AttemptSubmitRequest,
    AttemptResultResponse, QuizSessionSummaryResponse,
    QuestionResponse, QuestionOptionSchema, RetestRequest, RetestResponse
)
from app.services.quiz_service import QuizService

router = APIRouter(prefix="/quiz", tags=["Diagnostic Quiz"])

@router.post("/start", response_model=QuizStartResponse)
async def start_quiz(payload: QuizStartRequest, db: AsyncSession = Depends(get_db)):
    try:
        data = await QuizService.start_session(db, payload.topic_id, payload.student_id)
        # Map questions to Pydantic
        q_list = []
        for q in data["questions"]:
            opts = [QuestionOptionSchema(**opt) for opt in q.options] if isinstance(q.options, list) else []
            q_list.append(QuestionResponse(
                id=q.id,
                concept_id=q.concept_id,
                concept_name=q.concept.name if q.concept else None,
                question_text=q.question_text,
                options=opts,
                difficulty=q.difficulty
            ))
        return QuizStartResponse(
            session_id=data["session_id"],
            topic_id=data["topic_id"],
            student_id=data["student_id"],
            questions=q_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/submit-answer", response_model=AttemptResultResponse)
async def submit_answer(payload: AttemptSubmitRequest, db: AsyncSession = Depends(get_db)):
    try:
        result = await QuizService.submit_answer(
            session=db,
            session_id=payload.session_id,
            question_id=payload.question_id,
            concept_id=payload.concept_id,
            selected_option_id=payload.selected_option_id,
            confidence_score=payload.confidence_score,
            time_taken_seconds=payload.time_taken_seconds,
            student_id=payload.student_id
        )
        return AttemptResultResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete/{session_id}", response_model=QuizSessionSummaryResponse)
async def complete_quiz(session_id: str, db: AsyncSession = Depends(get_db)):
    try:
        summary = await QuizService.complete_session(db, session_id)
        return QuizSessionSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}", response_model=QuizSessionSummaryResponse)
async def get_session_results(session_id: str, db: AsyncSession = Depends(get_db)):
    try:
        summary = await QuizService.complete_session(db, session_id)
        return QuizSessionSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retest", response_model=RetestResponse)
async def retest_concept(payload: RetestRequest, db: AsyncSession = Depends(get_db)):
    student_id = payload.student_id or "student_demo_1"
    # Find questions for this specific concept
    from sqlalchemy.orm import joinedload
    q_stmt = select(Question).options(joinedload(Question.concept)).where(Question.concept_id == payload.concept_id)
    q_res = await db.execute(q_stmt)
    questions = list(q_res.scalars().all())

    # Create new diagnostic session
    c_stmt = select(Concept).where(Concept.id == payload.concept_id)
    c_res = await db.execute(c_stmt)
    concept = c_res.scalar_one_or_none()
    topic_id = concept.topic_id if concept else "topic_func_rec"

    diag_session = DiagnosticSession(
        student_id=student_id,
        topic_id=topic_id,
        status="in_progress"
    )
    db.add(diag_session)
    await db.flush()

    q_list = []
    for q in questions:
        opts = [QuestionOptionSchema(**opt) for opt in q.options] if isinstance(q.options, list) else []
        q_list.append(QuestionResponse(
            id=q.id,
            concept_id=q.concept_id,
            concept_name=q.concept.name if q.concept else None,
            question_text=q.question_text,
            options=opts,
            difficulty=q.difficulty
        ))

    return RetestResponse(
        session_id=diag_session.id,
        concept_id=payload.concept_id,
        questions=q_list
    )
