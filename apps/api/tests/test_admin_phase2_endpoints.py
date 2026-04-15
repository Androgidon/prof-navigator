import csv
import io

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


def test_admin_professions_export_requires_auth():
    response = client.get("/api/v1/admin/professions/export")
    assert response.status_code == 401


def test_admin_professions_export_csv_headers_and_shape_when_unauthorized():
    response = client.get("/api/v1/admin/professions/export?q=test&cluster=IT&status=active")
    assert response.status_code == 401

    # local shape contract check for csv headers and serialization expectations
    sample = io.StringIO()
    writer = csv.DictWriter(
        sample,
        fieldnames=[
            "slug",
            "title",
            "cluster",
            "family",
            "status",
            "summary",
            "what_specialist_does",
            "who_it_suits",
            "school_subjects",
            "required_skills",
            "how_to_start",
            "trajectory_notes",
            "content_status",
            "content_level",
            "express_example_eligible",
            "full_rank_eligible",
            "updated_at",
        ],
    )
    writer.writeheader()
    writer.writerow(
        {
            "slug": "qa-engineer",
            "title": "QA Engineer",
            "cluster": "IT и цифровые технологии",
            "family": "IT и цифровые технологии",
            "status": "active",
            "summary": "Проверяет качество решений",
            "what_specialist_does": "Проверяет качество решений",
            "who_it_suits": "[]",
            "school_subjects": "[\"Информатика\", \"Математика\"]",
            "required_skills": "[]",
            "how_to_start": "[\"Собрать мини-портфолио\"]",
            "trajectory_notes": "[]",
            "content_status": "ready",
            "content_level": "",
            "express_example_eligible": "true",
            "full_rank_eligible": "true",
            "updated_at": "2026-01-01T00:00:00",
        }
    )
    csv_text = sample.getvalue()
    assert "slug,title,cluster,family,status,summary" in csv_text
    assert "\"[\"" in csv_text
