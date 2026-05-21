import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app
from database.connection import get_db

client = TestClient(app)

today = date.today()
future_date = today + timedelta(days=30)


# Mocking database session
@pytest.fixture
def mock_db():
    mock_session = MagicMock()

    # In-memory fake DB
    fake_db = {}

    def fake_add(obj):
        if obj.cycle_id is None:
            obj.cycle_id = max(fake_db.keys(), default=0) + 1

        # Add fake stages (if your model supports a `stages` or `stage_names` field)
        obj.stage_names = ["Setup", "Self Appraisal"]
        fake_db[obj.cycle_id] = obj

    # Add this line inside mock_db()
    def fake_delete(obj):
        if hasattr(obj, "cycle_id") and obj.cycle_id in fake_db:
            del fake_db[obj.cycle_id]

    def fake_query(*args, **kwargs):
        class Query:
            def join(self, *args, **kwargs):
                return self  # allow chaining

            def all(self):
                return list(fake_db.values())

            def filter(self, *args, **kwargs):
                class Filter:
                    def first(inner_self):
                        condition = args[0]
                        cycle_id = (
                            condition.right.value
                            if hasattr(condition.right, "value")
                            else condition.right
                        )
                        return fake_db.get(cycle_id, None)

                    def distinct(inner_self):
                        return inner_self

                    def all(inner_self):
                        return list(fake_db.values())

                    def delete(inner_self):
                        condition = args[0]
                        cycle_id = (
                            condition.right.value
                            if hasattr(condition.right, "value")
                            else condition.right
                        )
                        if cycle_id in fake_db:
                            del fake_db[cycle_id]
                            return 1
                        return 0

                return Filter()

        return Query()

    mock_session.add.side_effect = fake_add
    mock_session.query.side_effect = fake_query
    mock_session.commit.return_value = None
    mock_session.refresh.side_effect = lambda obj: None
    mock_session.delete.side_effect = fake_delete

    return mock_session


# Override FastAPI dependency to use mock DB instead of real DB
@pytest.fixture(autouse=True)
def override_dependency(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    yield
    app.dependency_overrides.clear()


def create_fake_inactive_cycle(cycle_id=100, name="Mid year Review cycle"):
    class FakeCycle:
        def __init__(self):
            self.cycle_id = cycle_id
            self.cycle_name = name
            self.description = "To assess employees annually"
            self.status = "inactive"
            self.start_date_of_cycle = today
            self.end_date_of_cycle = future_date
            self.stage_name = "Setup"
            self.start_date_of_stage = today
            self.end_date_of_stage = today + timedelta(days=2)

    return FakeCycle()


def create_fake_active_cycle(cycle_id=200, name="Annual Review cycle"):
    class FakeCycle:
        def __init__(self):
            self.cycle_id = cycle_id
            self.cycle_name = name
            self.description = "To assess employees annually"
            self.status = "active"
            self.start_date_of_cycle = today
            self.end_date_of_cycle = future_date
            self.stage_name = "Setup"
            self.start_date_of_stage = today
            self.end_date_of_stage = today + timedelta(days=2)

    return FakeCycle()


# 1) Create a new cycle
# Input data
valid_payload = {
    "cycle_id": 2,
    "cycle_name": "Mid year Review cycle",
    "description": "To assess employees annually",
    "status": "inactive",
    "start_date_of_cycle": str(today),
    "end_date_of_cycle": str(future_date),
}


# For successful creation
def test_create_cycle():
    response = client.post("/appraisal_cycle", json=valid_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["cycle_name"] == valid_payload["cycle_name"]
    assert data["status"] == valid_payload["status"]
    assert "cycle_id" in data


# For invalid end date
def test_create_cycle_invalid_date_range():
    invalid_dates_payload = valid_payload.copy()
    invalid_dates_payload["start_date_of_cycle"] = str(today)
    invalid_dates_payload["end_date_of_cycle"] = str(today - timedelta(days=1))
    response = client.post("/appraisal_cycle", json=invalid_dates_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "End date cannot be before start date."


# 2) Get all cycles
def test_get_cycles(mock_db):
    # Manually create and add a cycle to the fake DB
    cycle = create_fake_inactive_cycle()
    mock_db.add(cycle)

    response = client.get("/appraisal_cycle")
    assert response.status_code == 200
    # print(response.json())


# 3) Get all cycles with stage names
def test_get_cycles_with_stage_names(mock_db):
    cycle = create_fake_inactive_cycle()
    mock_db.add(cycle)

    response = client.get("/appraisal_cycle/with-stage-names")
    assert response.status_code == 200
    # print(response.json())


# 4) Get cycle by ID
# For existing cycle ID
def test_get_cycle_by_id(mock_db):
    cycle = create_fake_inactive_cycle()
    mock_db.add(cycle)

    response = client.get(f"/appraisal_cycle/{cycle.cycle_id}")
    assert response.status_code == 200
    # print(response.json())


# For non-existing cycle ID
def test_get_cycle_by_invalid_id(mock_db):
    cycle = create_fake_inactive_cycle()
    mock_db.add(cycle)

    response = client.get(f"/appraisal_cycle/110")

    assert response.status_code == 404
    assert response.json()["detail"] == "Cycle not found"


# 5) Delete cycle by ID
# For existing cycle ID
def test_delete_cycle_by_id(mock_db):
    cycle = create_fake_inactive_cycle()
    mock_db.add(cycle)

    response = client.delete(f"/appraisal_cycle/{cycle.cycle_id}")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Cycle and related stages deleted successfully"
    }


# For non-existing cycle ID
def test_delete_cycle_by_invalid_id(mock_db):
    cycle = create_fake_inactive_cycle()
    mock_db.add(cycle)

    response = client.delete(f"/appraisal_cycle/110")
    assert response.status_code == 404
    assert response.json()["detail"] == "Cycle not found"


# Active or completed cycles should not be deleted
def test_delete_cycle_active_completed_status(mock_db):
    cycle = create_fake_active_cycle()
    mock_db.add(cycle)

    response = client.delete(f"/appraisal_cycle/{cycle.cycle_id}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot delete an active or completed cycle."


# 6) Get status of cycles by ID
# For existing cycle ID
def test_get_cycle_status(mock_db):
    cycle = create_fake_inactive_cycle()
    mock_db.add(cycle)

    response = client.get(f"/appraisal_cycle/status/{cycle.cycle_id}")
    assert response.status_code == 200
    # print(response.json())


# For non-existing cycle ID
def test_get_cycle_status_by_invalid_id(mock_db):
    cycle = create_fake_inactive_cycle()
    mock_db.add(cycle)

    response = client.get(f"/appraisal_cycle/status/110")
    assert response.status_code == 404
    assert response.json()["detail"] == "Appraisal cycle not found"


# 7) Get completed and  active cycles for which lead assessment stage is active or completed
def test_get_cycles_for_historic_report(mock_db):
    cycle = create_fake_active_cycle()
    mock_db.add(cycle)

    response = client.get("/appraisal_cycle/appraisal-cycles/historic-report")
    assert response.status_code == 200
    # print(response.json())


# 8) Get completed and  active cycles for which self assessment stage is active or completed
def test_get_cycles_for_self_assessment_report(mock_db):
    cycle = create_fake_active_cycle()
    mock_db.add(cycle)

    response = client.get("/appraisal_cycle/appraisal-cycles/self-assessment-report")
    assert response.status_code == 200
    # print(response.json())
