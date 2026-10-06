from typing import List, Dict, Set, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Concept, Prerequisite, MasteryState

class GraphEngine:
    """
    Handles Prerequisite Knowledge Graph (Directed Acyclic Graph)
    operations and Root-Cause Traversal.
    """

    @staticmethod
    async def get_prerequisites_for_concept(
        session: AsyncSession,
        concept_id: str
    ) -> List[Concept]:
        """Returns direct prerequisites for a given concept."""
        stmt = (
            select(Concept)
            .join(Prerequisite, Prerequisite.prerequisite_concept_id == Concept.id)
            .where(Prerequisite.concept_id == concept_id)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_all_ancestor_prerequisites(
        session: AsyncSession,
        concept_id: str
    ) -> List[Tuple[Concept, int]]:
        """
        Performs Depth-First Search (DFS) to find all upstream prerequisites,
        returning a list of (Concept, depth_distance) tuples.
        """
        visited: Set[str] = set()
        ancestors: List[Tuple[Concept, int]] = []

        async def _dfs(current_id: str, depth: int):
            direct_prereqs = await GraphEngine.get_prerequisites_for_concept(session, current_id)
            for prereq in direct_prereqs:
                if prereq.id not in visited:
                    visited.add(prereq.id)
                    ancestors.append((prereq, depth))
                    await _dfs(prereq.id, depth + 1)

        await _dfs(concept_id, 1)
        return ancestors

    @staticmethod
    async def detect_root_cause_gap(
        session: AsyncSession,
        student_id: str,
        target_concept_id: str
    ) -> Optional[Tuple[Concept, float, str]]:
        """
        When a student struggles with target_concept_id, inspects all upstream
        prerequisites in dependency order. If an ancestor prerequisite has
        mastery < 60%, it is flagged as the probable root cause!

        Returns: (PrerequisiteConcept, mastery_score, explanation) or None
        """
        ancestors = await GraphEngine.get_all_ancestor_prerequisites(session, target_concept_id)
        if not ancestors:
            return None

        # Sort ancestors by depth (deepest foundational concepts first)
        ancestors.sort(key=lambda x: x[1], reverse=True)

        for prereq_concept, depth in ancestors:
            # Query student's mastery for this prerequisite
            stmt = select(MasteryState).where(
                MasteryState.student_id == student_id,
                MasteryState.concept_id == prereq_concept.id
            )
            res = await session.execute(stmt)
            mastery_state = res.scalar_one_or_none()
            score = mastery_state.mastery_score if mastery_state else 0.0

            if score < 60.0:
                explanation = (
                    f"Found upstream prerequisite gap in '{prereq_concept.name}' (Mastery: {score:.1f}%). "
                    f"Difficulty in the target concept likely stems from this missing foundational link."
                )
                return (prereq_concept, score, explanation)

        return None

    @staticmethod
    async def calculate_prerequisite_health_index(
        session: AsyncSession,
        student_id: str,
        concept_id: str
    ) -> float:
        """
        Calculates the average mastery percentage (0.0 to 100.0) of
        immediate direct prerequisites. Returns 100.0 if no prerequisites exist.
        """
        direct_prereqs = await GraphEngine.get_prerequisites_for_concept(session, concept_id)
        if not direct_prereqs:
            return 100.0

        total_score = 0.0
        count = 0
        for p in direct_prereqs:
            stmt = select(MasteryState).where(
                MasteryState.student_id == student_id,
                MasteryState.concept_id == p.id
            )
            res = await session.execute(stmt)
            m = res.scalar_one_or_none()
            total_score += (m.mastery_score if m else 50.0)
            count += 1

        return round(total_score / count, 1) if count > 0 else 100.0
