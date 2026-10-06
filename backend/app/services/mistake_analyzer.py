from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import Mistake, Attempt, Question, Concept
from app.services.graph_engine import GraphEngine

class MistakeAnalyzer:
    """
    Analyzes incorrect answers, identifies repeated patterns,
    flags misconceptions, and maps mistakes to prerequisite gaps.
    """

    @staticmethod
    async def record_and_analyze_mistake(
        session: AsyncSession,
        attempt: Attempt,
        question: Question
    ) -> Mistake:
        """
        Extracts the misconception tag from the chosen option and determines
        if this is a repeated error pattern.
        """
        # Find misconception tag from question.options
        misconception_tag = "general_logic_error"
        if isinstance(question.options, list):
            for opt in question.options:
                if opt.get("id") == attempt.selected_option_id:
                    misconception_tag = opt.get("misconception_tag", "general_logic_error")
                    break

        # Check if the student made this exact misconception previously
        stmt = (
            select(func.count(Mistake.id))
            .where(
                Mistake.student_id == attempt.student_id,
                Mistake.misconception_tag == misconception_tag
            )
        )
        res = await session.execute(stmt)
        previous_count = res.scalar() or 0

        is_repeated = previous_count >= 1

        mistake = Mistake(
            attempt_id=attempt.id,
            student_id=attempt.student_id,
            concept_id=attempt.concept_id,
            misconception_tag=misconception_tag,
            is_repeated=is_repeated
        )
        session.add(mistake)
        await session.flush()
        return mistake

    @staticmethod
    async def get_student_mistake_history(
        session: AsyncSession,
        student_id: str
    ) -> List[Dict[str, Any]]:
        """Returns all recorded mistakes with rich diagnostic context."""
        stmt = (
            select(Mistake, Attempt, Question, Concept)
            .join(Attempt, Mistake.attempt_id == Attempt.id)
            .join(Question, Attempt.question_id == Question.id)
            .join(Concept, Attempt.concept_id == Concept.id)
            .where(Mistake.student_id == student_id)
            .order_by(Mistake.created_at.desc())
        )
        results = await session.execute(stmt)
        rows = results.all()

        mistakes_list = []
        for mistake, attempt, question, concept in rows:
            # Check repeat count
            count_stmt = (
                select(func.count(Mistake.id))
                .where(
                    Mistake.student_id == student_id,
                    Mistake.misconception_tag == mistake.misconception_tag
                )
            )
            count_res = await session.execute(count_stmt)
            repeat_count = count_res.scalar() or 1

            # Check root cause prerequisite
            root_cause = await GraphEngine.detect_root_cause_gap(session, student_id, concept.id)
            root_prereq_name = root_cause[0].name if root_cause else None

            # Determine diagnosis level
            if mistake.is_repeated and root_prereq_name:
                diagnosis_level = "HIGH CONFIDENCE"
                explanation = (
                    f"Repeated error pattern ({repeat_count}x): '{mistake.misconception_tag.replace('_', ' ').title()}'. "
                    f"Underlying prerequisite '{root_prereq_name}' has low mastery."
                )
            elif mistake.is_repeated:
                diagnosis_level = "LIKELY"
                explanation = f"Repeated error pattern ({repeat_count}x): '{mistake.misconception_tag.replace('_', ' ').title()}'."
            else:
                diagnosis_level = "UNCERTAIN"
                explanation = f"First observed occurrence of '{mistake.misconception_tag.replace('_', ' ').title()}'."

            mistakes_list.append({
                "id": mistake.id,
                "concept_id": concept.id,
                "concept_name": concept.name,
                "question_text": question.question_text,
                "selected_answer": attempt.selected_option_id,
                "correct_answer": question.correct_option_id,
                "misconception_tag": mistake.misconception_tag,
                "is_repeated": mistake.is_repeated,
                "repeat_count": repeat_count,
                "root_cause_prerequisite": root_prereq_name,
                "diagnosis_level": diagnosis_level,
                "explanation": explanation,
                "timestamp": mistake.created_at.isoformat()
            })

        return mistakes_list
