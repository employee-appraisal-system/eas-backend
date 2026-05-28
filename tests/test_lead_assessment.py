import pytest
from fastapi.testclient import TestClient
from fastapi import status
import sys
import os
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app
from models.appraisal_cycle import AppraisalCycle

client = TestClient(app)


# Mocking database session
@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def valid_request_payload():
    return {
        "cycle_id": 1,
        "employee_id": 123,
        "ratings": [{"parameter_id": 1, "parameter_rating": 4}],
        "discussion_date": "2025-05-01",
    }


#  Test: Successful save
@patch("routes.lead_assessment.get_db")
@patch("services.lead_assessment.save_lead_assessment_rating_service")
def test_save_rating_success(mock_service, mock_get_db, valid_request_payload, mock_db):
    mock_get_db.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = AppraisalCycle(
        cycle_id=1, status="active"
    )

    mock_service.return_value = {
        "message": "Lead assessment rating saved successfully."
    }

    response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Lead assessment rating saved successfully."}


#  Test: Appraisal cycle not found
@patch("routes.lead_assessment.get_db")
def test_save_rating_cycle_not_found(mock_get_db, valid_request_payload, mock_db):
    mock_get_db.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = None

    response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Appraisal cycle not found"


#  Test: Appraisal cycle is not active
@patch("routes.lead_assessment.get_db")
def test_save_rating_inactive_cycle(mock_get_db, valid_request_payload, mock_db):
    mock_get_db.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = AppraisalCycle(
        cycle_id=1, status="completed"
    )

    response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "The selected appraisal cycle is not active."


#  Test: No allocation found
@patch("routes.lead_assessment.get_db")
@patch("services.lead_assessment.save_lead_assessment_rating_service")
def test_save_rating_no_allocation(
    mock_service, mock_get_db, valid_request_payload, mock_db
):
    mock_get_db.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = AppraisalCycle(
        cycle_id=1, status="active"
    )

    mock_service.side_effect = ValueError("No allocation found")

    response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert (
        response.json()["detail"]
        == "No allocation found for the selected cycle and employee."
    )


# Test: Internal server error
@patch("routes.lead_assessment.get_db")
@patch("services.lead_assessment.save_lead_assessment_rating_service")
def test_save_rating_internal_error(
    mock_service, mock_get_db, valid_request_payload, mock_db
):
    mock_get_db.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = AppraisalCycle(
        cycle_id=1, status="active"
    )

    mock_service.side_effect = Exception("Unexpected error")

    response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Internal server error."
