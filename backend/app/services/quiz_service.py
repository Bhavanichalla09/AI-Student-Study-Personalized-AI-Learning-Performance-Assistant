from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from app.models import (
    DiagnosticSession, Question, Attempt, Mistake,
    ConfidenceMetric, MasteryState, Concept, Student
)
from app.services.mistake_analyzer import MistakeAnalyzer
from app.services.mastery_service import MasteryService
from app.services.calibration_engine import CalibrationEngine

class QuizService:
    @staticmethod
    async def start_session(
        session: AsyncSession,
        topic_id: str,
        student_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # Default to demo student if none supplied
        if not student_id:
            s_stmt = select(Student).limit(1)
            s_res = await session.execute(s_stmt)
            student = s_res.scalar_one_or_none()
            student_id = student.id if student else "demo-student-id"

        diag_session = DiagnosticSession(
            student_id=student_id,
            topic_id=topic_id,
            status="in_progress"
        )
        session.add(diag_session)
        await session.flush()

        # Fetch questions for this topic's concepts
        q_stmt = (
            select(Question)
            .options(joinedload(Question.concept))
            .join(Concept, Question.concept_id == Concept.id)
            .where(Concept.topic_id == topic_id)
            .order_by(Concept.sequence_order.asc(), Question.difficulty.asc())
        )
        q_res = await session.execute(q_stmt)
        questions = list(q_res.scalars().all())

        return {
            "session_id": diag_session.id,
            "student_id": student_id,
            "topic_id": topic_id,
            "questions": questions
        }

    @staticmethod
    async def submit_answer(
        session: AsyncSession,
        session_id: str,
        question_id: str,
        concept_id: str,
        selected_option_id: str,
        confidence_score: int,
        time_taken_seconds: int = 0,
        student_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # Fetch question
        q_stmt = select(Question).where(Question.id == question_id)
        q_res = await session.execute(q_stmt)
        question = q_res.scalar_one_or_none()
        if not question:
            raise ValueError(f"Question {question_id} not found")

        # Fetch session to get student_id if not passed
        if not student_id:
            s_stmt = select(DiagnosticSession).where(DiagnosticSession.id == session_id)
            s_res = await session.execute(s_stmt)
            diag_session = s_res.scalar_one_or_none()
            student_id = diag_session.student_id if diag_session else "demo-student-id"

        is_correct = (selected_option_id.strip().upper() == question.correct_option_id.strip().upper())

        # Record Attempt
        attempt = Attempt(
            session_id=session_id,
            student_id=student_id,
            question_id=question_id,
            concept_id=concept_id,
            selected_option_id=selected_option_id,
            is_correct=is_correct,
            confidence_score=confidence_score,
            time_taken_seconds=time_taken_seconds
        )
        session.add(attempt)
        await session.flush()

        misconception_tag = None
        if not is_correct:
            # Record and analyze mistake
            mistake = await MistakeAnalyzer.record_and_analyze_mistake(
                session, attempt, question
            )
            misconception_tag = mistake.misconception_tag

        # Update Confidence Metric for this concept
        stmt_concept_attempts = select(Attempt).where(
            Attempt.student_id == student_id,
            Attempt.concept_id == concept_id
        )
        ca_res = await session.execute(stmt_concept_attempts)
        all_concept_attempts = list(ca_res.scalars().all())

        total_ca = len(all_concept_attempts)
        avg_conf = sum(a.confidence_score for a in all_concept_attempts) / total_ca
        avg_acc = (sum(1 for a in all_concept_attempts if a.is_correct) / total_ca) * 100.0
        gap = CalibrationEngine.calculate_gap(avg_conf, avg_acc)
        cat = CalibrationEngine.classify_calibration(gap)

        stmt_cm = select(ConfidenceMetric).where(
            ConfidenceMetric.student_id == student_id,
            ConfidenceMetric.concept_id == concept_id
        )
        cm_res = await session.execute(stmt_cm)
        cm = cm_res.scalar_one_or_none()
        if cm:
            cm.avg_confidence = avg_conf
            cm.avg_accuracy = avg_acc
            cm.calibration_gap = gap
            cm.calibration_category = cat
            cm.sample_count = total_ca
        else:
            cm = ConfidenceMetric(
                student_id=student_id,
                concept_id=concept_id,
                avg_confidence=avg_conf,
                avg_accuracy=avg_acc,
                calibration_gap=gap,
                calibration_category=cat,
                sample_count=total_ca
            )
            session.add(cm)

        # Update Concept Mastery
        await MasteryService.update_concept_mastery(session, student_id, concept_id)

        return {
            "attempt_id": attempt.id,
            "question_id": question_id,
            "concept_id": concept_id,
            "is_correct": is_correct,
            "correct_option_id": question.correct_option_id,
            "explanation": question.explanation,
            "confidence_score": confidence_score,
            "misconception_detected": misconception_tag
        }

    @staticmethod
    async def complete_session(
        session: AsyncSession,
        session_id: str
    ) -> Dict[str, Any]:
        s_stmt = select(DiagnosticSession).where(DiagnosticSession.id == session_id)
        s_res = await session.execute(s_stmt)
        diag_session = s_res.scalar_one_or_none()
        if not diag_session:
            raise ValueError(f"Session {session_id} not found")

        diag_session.status = "completed"
        diag_session.completed_at = datetime.utcnow()

        # Fetch all attempts
        att_stmt = select(Attempt, Question).join(Question, Attempt.question_id == Question.id).where(Attempt.session_id == session_id)
        att_res = await session.execute(att_stmt)
        rows = att_res.all()

        total = len(rows)
        correct = sum(1 for a, _ in rows if a.is_correct)
        accuracy = (correct / total * 100.0) if total > 0 else 0.0
        avg_conf = (sum(a.confidence_score for a, _ in rows) / total) if total > 0 else 0.0
        gap = CalibrationEngine.calculate_gap(avg_conf, accuracy)

        attempts_data = []
        for a, q in rows:
            attempts_data.append({
                "attempt_id": a.id,
                "question_id": a.question_id,
                "concept_id": a.concept_id,
                "is_correct": a.is_correct,
                "correct_option_id": q.correct_option_id,
                "explanation": q.explanation,
                "confidence_score": a.confidence_score,
                "misconception_detected": None
            })

        return {
            "session_id": session_id,
            "topic_id": diag_session.topic_id,
            "total_questions": total,
            "correct_count": correct,
            "accuracy_percentage": round(accuracy, 1),
            "avg_confidence": round(avg_conf, 1),
            "calibration_gap": gap,
            "attempts": attempts_data
        }
