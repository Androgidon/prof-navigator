from fastapi.testclient import TestClient

from app.main import create_app


client = TestClient(create_app())


def test_express_pipeline_complete_and_reuse_result():
    start = client.post("/api/v1/assessments/start", json={"assessment_slug": "express_v1"})
    assert start.status_code == 200
    start_data = start.json()
    session_id = start_data["session_id"]

    answer_1 = client.post(
        f"/api/v1/assessments/{session_id}/answer",
        json={"question_id": "exp_interest_01", "answer": {"value": 75}},
    )
    assert answer_1.status_code == 200

    answer_2 = client.post(
        f"/api/v1/assessments/{session_id}/answer",
        json={"question_id": "exp_interest_05", "answer": {"key": "a"}},
    )
    assert answer_2.status_code == 200

    answer_3 = client.post(
        f"/api/v1/assessments/{session_id}/answer",
        json={"question_id": "exp_task_01", "answer": {"key": "c"}},
    )
    assert answer_3.status_code == 200

    complete_1 = client.post(f"/api/v1/assessments/{session_id}/complete")
    assert complete_1.status_code == 200
    result_id = complete_1.json()["result_id"]

    complete_2 = client.post(f"/api/v1/assessments/{session_id}/complete")
    assert complete_2.status_code == 200
    assert complete_2.json()["result_id"] == result_id

    result = client.get(f"/api/v1/assessments/results/{result_id}")
    assert result.status_code == 200
    data = result.json()

    assert data["status"] == "completed"
    assert data["assessment_slug"] == "express_v1"
    assert len(data["recommendations"]) == 10
    assert data["profile_summary"]["preliminary"] in {True, False}
    assert data["work_style"]["preliminary"] == data["profile_summary"]["preliminary"]
    assert all(item["preliminary"] == data["profile_summary"]["preliminary"] for item in data["top_strengths"])
    assert data["confidence"]["starter_dataset_limited"] == data["profile_summary"]["starter_dataset_limited"]
