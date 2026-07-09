from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_determine_wage_level_valid_request():
    response = client.post(
        "/wage-level/determine",
        json={
            "soc_code": "15-1252.00",
            "required_education": "bachelors",
            "required_experience_years": 0,
            "supervises_others": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["wage_level"] == "Level I"
    assert body["occupation_title"] == "Software Developers"
    assert "disclaimer" in body


def test_determine_wage_level_unknown_soc_code_returns_404():
    response = client.post(
        "/wage-level/determine",
        json={
            "soc_code": "00-0000.00",
            "required_education": "bachelors",
            "required_experience_years": 0,
            "supervises_others": False,
        },
    )
    assert response.status_code == 404


def test_determine_wage_level_missing_fields_returns_422():
    response = client.post("/wage-level/determine", json={"soc_code": "15-1252.00"})
    assert response.status_code == 422


def test_determine_wage_level_interviewer_payload_shape():
    response = client.post(
        "/wage-level/determine",
        json={
            "jobTitle": "Software Engineer",
            "socCode": "15-1252",
            "workLocation": {"state": "California", "city": "San Jose"},
            "education": "Bachelor",
            "experienceYears": 3,
            "specialSkills": ["Java", "Spring Boot", "AWS"],
            "supervisoryDuties": False,
            "employmentType": "Full-time",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["wage_level"] == "Level III"
    assert body["occupation_title"] == "Software Developers"
    assert body["job_title"] == "Software Engineer"
    assert body["work_location"] == {"state": "California", "city": "San Jose"}
    assert body["employment_type"] == "Full-time"


def test_occupations_search():
    response = client.get("/occupations/search", params={"q": "software"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert any(r["soc_code"] == "15-1252.00" for r in results)
