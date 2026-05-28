import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import date
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app
from models.appraisal_cycle import AppraisalCycle
from models.employee_allocation import EmployeeAllocation
from models.stages import Stage
from models.parameters import Parameter
from models.lead_assessment import LeadAssessmentRating

client = TestClient(app)


# Override get_db with a mock
@pytest.fixture
def mock_db_session(monkeypatch):
    mock_db = MagicMock()

    # Mock data
    mock_cycle = AppraisalCycle(cycle_id=1, status="active")
    mock_allocation = EmployeeAllocation(allocation_id=1, cycle_id=1, employee_id=101)
    mock_stage = Stage(
        cycle_id=1,
        stage_name="Lead Assessment",
        start_date_of_stage=date(2025, 5, 1),
        end_date_of_stage=date(2025, 5, 31),
    )
    mock_parameter = Parameter(parameter_id=1)

    # db.query(...).filter(...).first()
    def query_side_effect(model):
        query_mock = MagicMock()
        if model == AppraisalCycle:
            query_mock.filter.return_value.first.return_value = mock_cycle
        elif model == EmployeeAllocation:
            query_mock.filter.return_value.first.return_value = mock_allocation
        elif model == Stage:
            query_mock.filter.return_value.first.return_value = mock_stage
        elif model == Parameter:
            query_mock.filter.return_value.first.return_value = mock_parameter
        elif model == LeadAssessmentRating:
            query_mock.filter.return_value.first.return_value = None
        return query_mock

    mock_db.query.side_effect = query_side_effect

    monkeypatch.setattr("database.connection.get_db", lambda: mock_db)
    return mock_db


def test_save_rating_success(mock_db_session):
    payload = {
        "cycle_id": 1,
        "employee_id": 101,
        "ratings": [
            {"parameter_id": 1, "parameter_rating": 4, "specific_input": "Good effort"}
        ],
        "discussion_date": "2025-05-12",
    }

    response = client.post("/lead_assessment/save_rating", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] in [
        "Lead assessment rating saved successfully.",
        "No changes detected.",
    ]
