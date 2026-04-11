from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_admin_professions_requires_auth():
    response = client.get("/api/v1/admin/professions")
    assert response.status_code == 401


def test_admin_matrix_requires_auth():
    response = client.get("/api/v1/admin/matrix")
    assert response.status_code == 401


def test_admin_matrix_preview_requires_auth():
    response = client.post(
        "/api/v1/admin/matrix/preview",
        json={
            "profile_scores": {"analytical": 50},
            "target_profile_json": {"analytical": 50},
            "dimension_weights_json": {"analytical": 1},
            "critical_dimensions": [],
            "cluster": "",
        },
    )
    assert response.status_code == 401
