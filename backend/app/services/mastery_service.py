from typing import Tuple, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import MasteryState, Attempt, Mistake, TeachBackAttempt, Concept
from app.services.graph_engine import GraphEngine

class MasteryService:
    """
    Computes concept mastery score using the documented multi-signal heuristic:
    Mastery = (40% * Quiz) + (20% * Recent/Mistakes) + (20% * Teach-Back) + (10% * Prerequisites) + (10% * History)
    """

    @staticmethod
    def classify_mastery_level(score: float) -> str:
        if score >= 80.0:
            return "strong"
        elif score >= 50.0:
            return "developing"
        return "critical"

    @staticmethod
    async def update_concept_mastery(
        session: AsyncSession,
        student_id: str,
        concept_id: str
    ) -> MasteryState:
        """
        Recalculates and persists the updated mastery state for a concept.
        """
        # 1. Quiz Accuracy (Q)
        stmt_attempts = select(Attempt).where(
            Attempt.student_id == student_id,
            Attempt.concept_id == concept_id
        )
        res_attempts = await session.execute(stmt_attempts)
        attempts = res_attempts.scalars().all()

        if attempts:
            correct_count = sum(1 for a in attempts if a.is_correct)
            quiz_accuracy = (correct_count / len(attempts)) * 100.0
        else:
            quiz_accuracy = 50.0 # Neutral baseline if unattempted

        # 2. Recent Performance & Repeated Mistakes (R)
        # Check repeated mistakes on this concept
        stmt_mistakes = select(Mistake).where(
            Mistake.student_id == student_id,
            Mistake.concept_id == concept_id
        )
        res_mistakes = await session.execute(stmt_mistakes)
        mistakes = res_mistakes.scalars().all()
        repeated_mistakes = sum(1 for m in mistakes if m.is_repeated)

        if not mistakes:
            recent_score = 100.0
        elif repeated_mistakes > 0:
            recent_score = max(20.0, 100.0 - (repeated_mistakes * 25.0) - (len(mistakes) * 10.0))
        else:
            recent_score = max(40.0, 100.0 - (len(mistakes) * 15.0))

        # 3. Teach-Back Score (T)
        stmt_tb = (
            select(TeachBackAttempt)
            .where(
                TeachBackAttempt.student_id == student_id,
                TeachBackAttempt.concept_id == concept_id
            )
            .order_by(TeachBackAttempt.created_at.desc())
        )
        res_tb = await session.execute(stmt_tb)
        latest_tb = res_tb.scalars().first()
        teachback_score = float(latest_tb.overall_score) if latest_tb else quiz_accuracy

        # 4. Prerequisite Health Index (P)
        prereq_health = await GraphEngine.calculate_prerequisite_health_index(
            session, student_id, concept_id
        )

        # 5. History / Retention (H)
        history_score = quiz_accuracy

        # Multi-Signal Heuristic Sum
        raw_mastery = (
            (0.40 * quiz_accuracy) +
            (0.20 * recent_score) +
            (0.20 * teachback_score) +
            (0.10 * prereq_health) +
            (0.10 * history_score)
        )
        final_score = round(max(0.0, min(100.0, raw_mastery)), 1)
        level = MasteryService.classify_mastery_level(final_score)

        # Save or update mastery record
        stmt_existing = select(MasteryState).where(
            MasteryState.student_id == student_id,
            MasteryState.concept_id == concept_id
        )
        res_existing = await session.execute(stmt_existing)
        mastery_record = res_existing.scalar_one_or_none()

        if mastery_record:
            mastery_record.mastery_score = final_score
            mastery_record.mastery_level = level
        else:
            mastery_record = MasteryState(
                student_id=student_id,
                concept_id=concept_id,
                mastery_score=final_score,
                mastery_level=level
            )
            session.add(mastery_record)

        await session.flush()
        return mastery_record
