import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AI Student Study API"

@pytest.mark.asyncio
async def test_curriculum_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Subjects
        res_subj = await client.get("/api/subjects")
        assert res_subj.status_code == 200
        subjects = res_subj.json()
        assert len(subjects) >= 1
        subject_id = subjects[0]["id"]

        # Topics
        res_topics = await client.get(f"/api/subjects/{subject_id}/topics")
        assert res_topics.status_code == 200
        topics = res_topics.json()
        assert len(topics) >= 1
        topic_id = topics[0]["id"]

        # Concepts
        res_concepts = await client.get(f"/api/topics/{topic_id}/concepts")
        assert res_concepts.status_code == 200
        concepts = res_concepts.json()
        assert len(concepts) >= 8

@pytest.mark.asyncio
async def test_knowledge_map_and_diagnosis():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_map = await client.get("/api/learner/knowledge-map/topic_func_rec?student_id=student_demo_1")
        assert res_map.status_code == 200
        data = res_map.json()
        assert "overall_mastery" in data
        assert len(data["concepts"]) == 8

        # Test diagnosis for Return Values (c_ret)
        res_diag = await client.get("/api/learner/concept-diagnosis/c_ret?student_id=student_demo_1")
        assert res_diag.status_code == 200
        diag = res_diag.json()
        assert diag["code"] == "PY-RET"
        assert len(diag["why_evidence"]) > 0

@pytest.mark.asyncio
async def test_calibration_summary_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/confidence/summary?student_id=student_demo_1")
        assert res.status_code == 200
        calib = res.json()
        assert "overall_avg_confidence" in calib
        assert "calibration_gap" in calib
        assert len(calib["data_points"]) >= 5
