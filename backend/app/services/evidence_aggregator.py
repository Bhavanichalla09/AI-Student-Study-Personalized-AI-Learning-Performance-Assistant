from typing import Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import (
    DiagnosticEvidence, Attempt, Mistake, TeachBackAttempt,
    MasteryState, Concept, DiagnosticSession
)
from app.services.graph_engine import GraphEngine

class EvidenceAggregator:
    """
    Fuses multi-signal evidence, derives diagnosis confidence states
    (HIGH CONFIDENCE, LIKELY, UNCERTAIN, INSUFFICIENT EVIDENCE),
    and compiles the explainable 'Why?' evidence trail.
    """

    @staticmethod
    async def aggregate_concept_evidence(
        session: AsyncSession,
        student_id: str,
        concept_id: str
    ) -> Dict[str, Any]:
        # 1. Fetch Concept Info
        stmt_c = select(Concept).where(Concept.id == concept_id)
        res_c = await session.execute(stmt_c)
        concept = res_c.scalar_one_or_none()
        if not concept:
            raise ValueError(f"Concept {concept_id} not found")

        # 2. Fetch Quiz Attempts
        stmt_att = select(Attempt).where(
            Attempt.student_id == student_id,
            Attempt.concept_id == concept_id
        ).order_by(Attempt.created_at.desc())
        res_att = await session.execute(stmt_att)
        attempts = list(res_att.scalars().all())

        # 3. Fetch Mistakes
        stmt_m = select(Mistake).where(
            Mistake.student_id == student_id,
            Mistake.concept_id == concept_id
        )
        res_m = await session.execute(stmt_m)
        mistakes = list(res_m.scalars().all())
        repeated_mistakes = [m for m in mistakes if m.is_repeated]

        # 4. Fetch Teach-Back
        stmt_tb = select(TeachBackAttempt).where(
            TeachBackAttempt.student_id == student_id,
            TeachBackAttempt.concept_id == concept_id
        ).order_by(TeachBackAttempt.created_at.desc())
        res_tb = await session.execute(stmt_tb)
        latest_tb = res_tb.scalars().first()

        # 5. Fetch Prerequisite Root-Cause Gap
        root_cause_tuple = await GraphEngine.detect_root_cause_gap(session, student_id, concept_id)
        prereq_health = await GraphEngine.calculate_prerequisite_health_index(session, student_id, concept_id)

        # 6. Fetch Mastery
        stmt_mas = select(MasteryState).where(
            MasteryState.student_id == student_id,
            MasteryState.concept_id == concept_id
        )
        res_mas = await session.execute(stmt_mas)
        mastery = res_mas.scalar_one_or_none()
        mastery_score = mastery.mastery_score if mastery else 0.0
        mastery_level = mastery.mastery_level if mastery else "critical"

        # Calculate Statistics
        total_attempts = len(attempts)
        correct_attempts = sum(1 for a in attempts if a.is_correct)
        accuracy = (correct_attempts / total_attempts * 100.0) if total_attempts > 0 else 0.0
        avg_confidence = (sum(a.confidence_score for a in attempts) / total_attempts) if total_attempts > 0 else 0.0

        # Construct the "Why?" Evidence Trail
        why_evidence: List[Dict[str, Any]] = []

        # Signal A: Quiz
        if total_attempts == 0:
            why_evidence.append({
                "type": "quiz_data",
                "description": "No diagnostic questions attempted yet.",
                "is_positive": False
            })
        elif accuracy >= 75.0:
            why_evidence.append({
                "type": "quiz_data",
                "description": f"Strong quiz accuracy: {correct_attempts}/{total_attempts} questions correct ({accuracy:.0f}%).",
                "is_positive": True
            })
        else:
            failed_count = total_attempts - correct_attempts
            why_evidence.append({
                "type": "quiz_data",
                "description": f"{failed_count} of {total_attempts} diagnostic questions answered incorrectly ({accuracy:.0f}% accuracy).",
                "is_positive": False
            })

        # Signal B: Mistakes
        if repeated_mistakes:
            tags = set(m.misconception_tag.replace('_', ' ').title() for m in repeated_mistakes)
            why_evidence.append({
                "type": "repeated_mistake",
                "description": f"Repeated misconception detected: {', '.join(tags)}.",
                "is_positive": False
            })
        elif mistakes:
            why_evidence.append({
                "type": "single_mistake",
                "description": f"{len(mistakes)} isolated mistake pattern recorded.",
                "is_positive": False
            })

        # Signal C: Teach-Back
        if latest_tb:
            if latest_tb.overall_score >= 70:
                why_evidence.append({
                    "type": "teachback",
                    "description": f"Teach-back explanation demonstrated solid understanding (Score: {latest_tb.overall_score}%).",
                    "is_positive": True
                })
            else:
                why_evidence.append({
                    "type": "teachback",
                    "description": f"Teach-back missed key conceptual elements (Score: {latest_tb.overall_score}%). {latest_tb.misconception_details or ''}",
                    "is_positive": False
                })

        # Signal D: Prerequisites
        if root_cause_tuple:
            root_prereq, r_score, _ = root_cause_tuple
            why_evidence.append({
                "type": "prerequisite_gap",
                "description": f"Identified foundational gap in prerequisite '{root_prereq.name}' (Mastery: {r_score:.0f}%).",
                "is_positive": False
            })
        else:
            why_evidence.append({
                "type": "prerequisite_health",
                "description": f"Prerequisite health index is healthy ({prereq_health:.0f}%).",
                "is_positive": prereq_health >= 70.0
            })

        # Signal E: Confidence Calibration
        gap = avg_confidence - accuracy
        if gap > 15.0 and total_attempts > 0:
            why_evidence.append({
                "type": "calibration",
                "description": f"Overconfidence gap detected: Confidence was {avg_confidence:.0f}% while accuracy was {accuracy:.0f}% (Gap: +{gap:.0f}%).",
                "is_positive": False
            })
        elif gap < -15.0 and total_attempts > 0:
            why_evidence.append({
                "type": "calibration",
                "description": f"Underconfidence detected: Performed well ({accuracy:.0f}%) despite low self-confidence ({avg_confidence:.0f}%).",
                "is_positive": True
            })

        # Multi-Signal Confidence Classification
        if total_attempts < 2 and not latest_tb:
            diagnosis_state = "INSUFFICIENT EVIDENCE"
            diagnosis_confidence = 30.0
            rec_action = f"Complete at least 3 diagnostic questions on '{concept.name}' to generate an evidence-backed diagnosis."
        else:
            # Check agreement between negative signals
            negative_signals = sum(1 for w in why_evidence if not w["is_positive"])
            positive_signals = sum(1 for w in why_evidence if w["is_positive"])

            if negative_signals >= 3:
                diagnosis_state = "HIGH CONFIDENCE"
                diagnosis_confidence = 88.0 + min(10.0, total_attempts * 2.0)
                if root_cause_tuple:
                    rec_action = f"Review prerequisite '{root_cause_tuple[0].name}' first before retrying {concept.name}."
                else:
                    rec_action = f"Review core rules for {concept.name} and clear repeated misconceptions."
            elif negative_signals >= 2:
                diagnosis_state = "LIKELY"
                diagnosis_confidence = 72.0
                rec_action = f"Targeted practice recommended on {concept.name}."
            elif positive_signals > 0 and negative_signals > 0:
                diagnosis_state = "UNCERTAIN"
                diagnosis_confidence = 55.0
                rec_action = "Conflicting performance signals. Complete a teach-back or focused retest to clarify mastery."
            else:
                diagnosis_state = "HIGH CONFIDENCE"
                diagnosis_confidence = 92.0
                rec_action = f"Concept mastered ({mastery_score:.0f}%). Ready to advance to subsequent topics."

        return {
            "concept_id": concept_id,
            "concept_name": concept.name,
            "code": concept.code,
            "mastery_score": mastery_score,
            "mastery_level": mastery_level,
            "quiz_accuracy": accuracy,
            "teachback_score": float(latest_tb.overall_score) if latest_tb else 0.0,
            "prerequisite_health": prereq_health,
            "confidence_avg": avg_confidence,
            "why_evidence": why_evidence,
            "diagnosis_confidence": round(diagnosis_confidence, 1),
            "diagnosis_state": diagnosis_state,
            "recommended_action": rec_action,
            "root_cause": {
                "id": root_cause_tuple[0].id,
                "name": root_cause_tuple[0].name,
                "score": root_cause_tuple[1],
            } if root_cause_tuple else None
        }
