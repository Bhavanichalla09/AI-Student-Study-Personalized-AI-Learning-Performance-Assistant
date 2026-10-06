from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Subject, Topic, Concept, Prerequisite
from app.schemas.schemas import SubjectResponse, TopicResponse, ConceptResponse
from app.services.graph_engine import GraphEngine

router = APIRouter(tags=["Curriculum & Knowledge Graph"])

@router.get("/subjects", response_model=List[SubjectResponse])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    stmt = select(Subject)
    res = await db.execute(stmt)
    subjects = res.scalars().all()

    output = []
    for s in subjects:
        # Count topics
        count_stmt = select(func.count(Topic.id)).where(Topic.subject_id == s.id)
        c_res = await db.execute(count_stmt)
        t_count = c_res.scalar() or 0
        output.append(SubjectResponse(
            id=s.id,
            name=s.name,
            slug=s.slug,
            description=s.description,
            topics_count=t_count
        ))
    return output

@router.get("/subjects/{subject_id}/topics", response_model=List[TopicResponse])
async def list_topics(subject_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Topic).where(Topic.subject_id == subject_id).order_by(Topic.sequence_order)
    res = await db.execute(stmt)
    topics = res.scalars().all()

    output = []
    for t in topics:
        c_stmt = select(func.count(Concept.id)).where(Concept.topic_id == t.id)
        c_res = await db.execute(c_stmt)
        c_count = c_res.scalar() or 0
        output.append(TopicResponse(
            id=t.id,
            subject_id=t.subject_id,
            name=t.name,
            description=t.description,
            sequence_order=t.sequence_order,
            concepts_count=c_count
        ))
    return output

@router.get("/topics/{topic_id}/concepts", response_model=List[ConceptResponse])
async def list_concepts(topic_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Concept).where(Concept.topic_id == topic_id).order_by(Concept.sequence_order)
    res = await db.execute(stmt)
    return list(res.scalars().all())

@router.get("/graph/{topic_id}")
async def get_topic_graph(topic_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns nodes and edges for visualizing the prerequisite DAG.
    """
    c_stmt = select(Concept).where(Concept.topic_id == topic_id).order_by(Concept.sequence_order)
    c_res = await db.execute(c_stmt)
    concepts = list(c_res.scalars().all())
    concept_ids = [c.id for c in concepts]

    p_stmt = select(Prerequisite).where(Prerequisite.concept_id.in_(concept_ids))
    p_res = await db.execute(p_stmt)
    edges = list(p_res.scalars().all())

    nodes = [
        {
            "id": c.id,
            "code": c.code,
            "name": c.name,
            "difficulty": c.difficulty_level,
            "sequence_order": c.sequence_order
        }
        for c in concepts
    ]

    edge_list = [
        {
            "id": f"e_{e.prerequisite_concept_id}_{e.concept_id}",
            "source": e.prerequisite_concept_id,
            "target": e.concept_id,
            "relationship_type": e.relationship_type
        }
        for e in edges
    ]

    return {
        "topic_id": topic_id,
        "nodes": nodes,
        "edges": edge_list
    }

@router.get("/prerequisites/{concept_id}")
async def get_concept_prerequisites(concept_id: str, db: AsyncSession = Depends(get_db)):
    direct_prereqs = await GraphEngine.get_prerequisites_for_concept(db, concept_id)
    ancestors = await GraphEngine.get_all_ancestor_prerequisites(db, concept_id)

    return {
        "concept_id": concept_id,
        "direct_prerequisites": [
            {"id": p.id, "name": p.name, "code": p.code} for p in direct_prereqs
        ],
        "all_ancestor_prerequisites": [
            {"id": a[0].id, "name": a[0].name, "code": a[0].code, "depth": a[1]} for a in ancestors
        ]
    }
