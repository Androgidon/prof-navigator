from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_admin_me_requires_auth():
    response = client.get("/api/v1/admin/me")
    assert response.status_code == 401


def test_admin_assessments_requires_auth():
    response = client.get("/api/v1/admin/assessments")
    assert response.status_code == 401


def test_admin_questions_requires_auth():
    response = client.get("/api/v1/admin/questions")
    assert response.status_code == 401


def test_admin_preview_signal_works_without_auth_guard_for_router_guarded_scope_only():
    response = client.post(
        "/api/v1/admin/questions/preview-signal",
        json={
            "question_type": "likert",
            "options_json": [{"key": "1", "label": "x"}],
            "weights_by_dimension_json": {"analytical": 1},
            "answer": {"value": 75},
        },
    )
    assert response.status_code == 403 or response.status_code == 401
