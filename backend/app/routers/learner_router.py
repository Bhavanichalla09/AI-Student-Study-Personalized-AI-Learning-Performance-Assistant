from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Concept, ConfidenceMetric, MasteryState
from app.schemas.schemas import (
    KnowledgeMapResponse, ConceptMasteryItem,
    CalibrationSummaryResponse, CalibrationDataPoint, WhyEvidenceItem
)
from app.services.evidence_aggregator import EvidenceAggregator
from app.services.graph_engine import GraphEngine
from app.services.calibration_engine import CalibrationEngine

router = APIRouter(tags=["Learner Model & Evidence"])

@router.get("/learner/knowledge-map/{topic_id}", response_model=KnowledgeMapResponse)
async def get_knowledge_map(
    topic_id: str,
    student_id: Optional[str] = Query(default="student_demo_1"),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Fetch concepts for this topic
        c_stmt = select(Concept).where(Concept.topic_id == topic_id).order_by(Concept.sequence_order)
        c_res = await db.execute(c_stmt)
        concepts = list(c_res.scalars().all())

        concept_items: List[ConceptMasteryItem] = []
        total_mastery = 0.0

        for c in concepts:
            diag = await EvidenceAggregator.aggregate_concept_evidence(db, student_id, c.id)
            direct_prereqs = await GraphEngine.get_prerequisites_for_concept(db, c.id)

            prereq_list = []
            for dp in direct_prereqs:
                m_stmt = select(MasteryState).where(
                    MasteryState.student_id == student_id,
                    MasteryState.concept_id == dp.id
                )
                m_res = await db.execute(m_stmt)
                m_state = m_res.scalar_one_or_none()
                prereq_list.append({
                    "concept_id": dp.id,
                    "concept_name": dp.name,
                    "mastery_score": m_state.mastery_score if m_state else 50.0
                })

            why_list = [WhyEvidenceItem(**w) for w in diag["why_evidence"]]

            item = ConceptMasteryItem(
                concept_id=c.id,
                concept_name=c.name,
                code=c.code,
                mastery_score=diag["mastery_score"],
                mastery_level=diag["mastery_level"],
                quiz_accuracy=diag["quiz_accuracy"],
                teachback_score=diag["teachback_score"],
                prerequisite_health=diag["prerequisite_health"],
                confidence_avg=diag["confidence_avg"],
                prerequisites=prereq_list,
                why_evidence=why_list,
                diagnosis_confidence=diag["diagnosis_confidence"],
                diagnosis_state=diag["diagnosis_state"],
                recommended_action=diag["recommended_action"]
            )
            concept_items.append(item)
            total_mastery += diag["mastery_score"]

        overall = round(total_mastery / len(concepts), 1) if concepts else 0.0

        return KnowledgeMapResponse(
            topic_id=topic_id,
            student_id=student_id,
            overall_mastery=overall,
            concepts=concept_items
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/learner/concept-diagnosis/{concept_id}")
async def get_concept_diagnosis(
    concept_id: str,
    student_id: Optional[str] = Query(default="student_demo_1"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await EvidenceAggregator.aggregate_concept_evidence(db, student_id, concept_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/confidence/summary", response_model=CalibrationSummaryResponse)
async def get_calibration_summary(
    student_id: Optional[str] = Query(default="student_demo_1"),
    db: AsyncSession = Depends(get_db)
):
    try:
        stmt = (
            select(ConfidenceMetric, Concept)
            .join(Concept, ConfidenceMetric.concept_id == Concept.id)
            .where(ConfidenceMetric.student_id == student_id)
        )
        res = await db.execute(stmt)
        rows = res.all()

        points: List[CalibrationDataPoint] = []
        tot_conf = 0.0
        tot_acc = 0.0
        count = len(rows)

        for cm, concept in rows:
            points.append(CalibrationDataPoint(
                concept_name=concept.name,
                confidence=cm.avg_confidence,
                accuracy=cm.avg_accuracy,
                gap=cm.calibration_gap,
                category=cm.calibration_category,
                sample_size=cm.sample_count
            ))
            tot_conf += cm.avg_confidence
            tot_acc += cm.avg_accuracy

        overall_conf = round(tot_conf / count, 1) if count > 0 else 0.0
        overall_acc = round(tot_acc / count, 1) if count > 0 else 0.0
        overall_gap = CalibrationEngine.calculate_gap(overall_conf, overall_acc)
        overall_cat = CalibrationEngine.classify_calibration(overall_gap)

        if overall_cat == "overconfident":
            bias = "Overconfidence"
        elif overall_cat == "underconfident":
            bias = "Underconfidence"
        else:
            bias = "Calibrated"

        insight = CalibrationEngine.generate_insight(overall_conf, overall_acc, overall_cat)

        return CalibrationSummaryResponse(
            overall_avg_confidence=overall_conf,
            overall_avg_accuracy=overall_acc,
            calibration_gap=overall_gap,
            primary_bias=bias,
            data_points=points,
            insight_explanation=insight
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
