from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Recommendation, MasteryState, Concept
from app.services.graph_engine import GraphEngine

class RecommendationEngine:
    """
    Generates evidence-backed learning recommendations targeting root-cause
    prerequisite bottlenecks rather than superficial symptoms.
    """

    @staticmethod
    async def generate_recommendations_for_student(
        session: AsyncSession,
        student_id: str
    ) -> List[Recommendation]:
        # Fetch all critical or developing mastery states
        stmt = (
            select(MasteryState, Concept)
            .join(Concept, MasteryState.concept_id == Concept.id)
            .where(
                MasteryState.student_id == student_id,
                MasteryState.mastery_score < 75.0
            )
            .order_by(MasteryState.mastery_score.asc())
        )
        res = await session.execute(stmt)
        low_mastery_items = res.all()

        recommendations = []
        for mastery_state, concept in low_mastery_items:
            # Check for root cause prerequisite
            root_cause_tuple = await GraphEngine.detect_root_cause_gap(
                session, student_id, concept.id
            )

            if root_cause_tuple:
                root_concept, r_score, _ = root_cause_tuple
                title = f"Resolve Prerequisite Bottleneck: {root_concept.name}"
                reason = (
                    f"Your mastery in '{concept.name}' is {mastery_state.mastery_score:.0f}%, but the primary "
                    f"root cause is an upstream gap in '{root_concept.name}' ({r_score:.0f}% mastery)."
                )
                action_steps = [
                    f"1. Review the foundational rules of '{root_concept.name}' (5-minute review).",
                    f"2. Study how '{root_concept.name}' directly supplies inputs to '{concept.name}'.",
                    f"3. Complete 2 diagnostic practice problems on '{root_concept.name}'.",
                    f"4. Teach-back the concept in your own words to verify conceptual mastery."
                ]
                root_id = root_concept.id
                priority = "high"
            else:
                title = f"Strengthen Conceptual Foundation: {concept.name}"
                reason = f"Current mastery is at {mastery_state.mastery_score:.0f}%. Direct practice is required to address detected mistake patterns."
                action_steps = [
                    f"1. Review code syntax and execution trace for '{concept.name}'.",
                    f"2. Solve 3 targeted diagnostic questions.",
                    f"3. Explain the mechanism via the Teach-Back Studio."
                ]
                root_id = None
                priority = "high" if mastery_state.mastery_score < 50.0 else "medium"

            # Check if active recommendation already exists
            stmt_exist = select(Recommendation).where(
                Recommendation.student_id == student_id,
                Recommendation.target_concept_id == concept.id,
                Recommendation.is_completed == False
            )
            res_exist = await session.execute(stmt_exist)
            existing = res_exist.scalar_one_or_none()

            if existing:
                existing.title = title
                existing.reason = reason
                existing.action_steps = action_steps
                existing.priority = priority
                recommendations.append(existing)
            else:
                new_rec = Recommendation(
                    student_id=student_id,
                    target_concept_id=concept.id,
                    root_cause_concept_id=root_id,
                    title=title,
                    reason=reason,
                    action_steps=action_steps,
                    priority=priority
                )
                session.add(new_rec)
                recommendations.append(new_rec)

        await session.flush()
        return recommendations
