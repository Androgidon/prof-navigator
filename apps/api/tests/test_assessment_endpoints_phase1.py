from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_assessment_complete_returns_404_for_unknown_session():
    response = client.post("/api/v1/assessments/00000000-0000-0000-0000-000000000001/complete")
    assert response.status_code == 404


def test_assessment_result_returns_404_for_unknown_result():
    response = client.get("/api/v1/assessments/results/00000000-0000-0000-0000-000000000001")
    assert response.status_code == 404
