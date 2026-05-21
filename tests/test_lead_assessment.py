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


# import pytest
# from fastapi.testclient import TestClient
# from fastapi import status
# import sys
# import os
# from unittest.mock import MagicMock, patch
# from sqlalchemy.exc import SQLAlchemyError

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from main import app
# from models.appraisal_cycle import AppraisalCycle

# client = TestClient(app)

# # Mocking database session
# @pytest.fixture
# def mock_db():
#     return MagicMock()

# @pytest.fixture
# def valid_request_payload():
#     return {
#         "cycle_id": 1,
#         "employee_id": 123,
#         "ratings": [{"parameter_id": 1, "parameter_rating": 4}],
#         "discussion_date": "2025-05-01"
#     }

# #  Test: Successful save
# @patch("routes.lead_assessment.get_db")
# @patch("services.lead_assessment.save_lead_assessment_rating_service")
# def test_save_rating_success(mock_service, mock_get_db, valid_request_payload, mock_db):
#     mock_get_db.return_value = mock_db
#     mock_db.query.return_value.filter.return_value.first.return_value = AppraisalCycle(cycle_id=1, status="active")

#     mock_service.return_value = {"message": "Ratings saved successfully"}

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == {"message": "Ratings saved successfully"}

# #  Test: Appraisal cycle not found
# @patch("routes.lead_assessment.get_db")
# def test_save_rating_cycle_not_found(mock_get_db, valid_request_payload, mock_db):
#     mock_get_db.return_value = mock_db
#     mock_db.query.return_value.filter.return_value.first.return_value = None

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     assert response.json()["detail"] == "Appraisal cycle not found"

# #  Test: Appraisal cycle is not active
# @patch("routes.lead_assessment.get_db")
# def test_save_rating_inactive_cycle(mock_get_db, valid_request_payload, mock_db):
#     mock_get_db.return_value = mock_db
#     mock_db.query.return_value.filter.return_value.first.return_value = AppraisalCycle(cycle_id=1, status="completed")

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.json()["detail"] == "The selected appraisal cycle is not active."

# #  Test: No allocation found
# @patch("routes.lead_assessment.get_db")
# @patch("routes.lead_assessment.save_lead_assessment_rating_service")
# def test_save_rating_no_allocation(mock_service, mock_get_db, valid_request_payload, mock_db):
#     mock_get_db.return_value = mock_db
#     mock_db.query.return_value.filter.return_value.first.return_value = AppraisalCycle(cycle_id=1, status="active")

#     mock_service.side_effect = ValueError("No allocation found")

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     assert response.json()["detail"] == "No allocation found for the selected cycle and employee."

# # Test: Internal server error
# @patch("routes.lead_assessment.get_db")
# @patch("routes.lead_assessment.save_lead_assessment_rating_service")
# def test_save_rating_internal_error(mock_service, mock_get_db, valid_request_payload, mock_db):
#     mock_get_db.return_value = mock_db
#     mock_db.query.return_value.filter.return_value.first.return_value = AppraisalCycle(cycle_id=1, status="active")

#     mock_service.side_effect = Exception("Unexpected error")

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
#     assert response.json()["detail"] == "Internal server error."


# import pytest
# from fastapi.testclient import TestClient
# from fastapi import status
# import sys
# import os
# from unittest.mock import MagicMock, patch
# from sqlalchemy.exc import SQLAlchemyError

# # Set path to project root so we can import main, models, etc.
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from main import app
# from models.appraisal_cycle import AppraisalCycle

# client = TestClient(app)

# # Fixture: Mock DB session
# @pytest.fixture
# def mock_db():
#     return MagicMock()

# # Fixture: Valid request body
# @pytest.fixture
# def valid_request_payload():
#     return {
#         "cycle_id": 1,
#         "employee_id": 101,
#         "ratings": [{"parameter_id": 5, "parameter_rating": 4}],
#         "discussion_date": "2025-05-01"
#     }

# #  Successful save
# @patch("routes.lead_assessment.get_db")
# @patch("services.lead_assessment.save_lead_assessment_rating_service")
# def test_save_rating_success(mock_service, mock_get_db, valid_request_payload, mock_db):
#     mock_get_db.return_value = mock_db
#     mock_db.query.return_value.filter.return_value.first.return_value = AppraisalCycle(cycle_id=1, status="active")
#     mock_service.return_value = {"message": "Ratings saved successfully"}

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == {"message": "Ratings saved successfully"}

# #  Appraisal cycle not found
# @patch("routes.lead_assessment.get_db")
# def test_save_rating_cycle_not_found(mock_get_db, valid_request_payload, mock_db):
#     mock_get_db.return_value = mock_db
#     mock_db.query.return_value.filter.return_value.first.return_value = None

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     assert response.json()["detail"] == "Appraisal cycle not found"

# #  Appraisal cycle is not active
# @patch("routes.lead_assessment.get_db")
# def test_save_rating_inactive_cycle(mock_get_db, valid_request_payload, mock_db):
#     mock_get_db.return_value = mock_db
#     mock_db.query.return_value.filter.return_value.first.return_value = AppraisalCycle(cycle_id=1, status="completed")

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.json()["detail"] == "The selected appraisal cycle is not active."

# #  No allocation found
# @patch("routes.lead_assessment.get_db")
# @patch("services.lead_assessment.save_lead_assessment_rating_service")
# def test_save_rating_no_allocation(mock_service, mock_get_db, valid_request_payload, mock_db):
#     mock_get_db.return_value = mock_db
#     mock_db.query.return_value.filter.return_value.first.return_value = AppraisalCycle(cycle_id=1, status="active")
#     mock_service.side_effect = ValueError("No allocation found")

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     assert response.json()["detail"] == "No allocation found for the selected cycle and employee."

# #  Internal server error
# @patch("routes.lead_assessment.get_db")
# @patch("services.lead_assessment.save_lead_assessment_rating_service")
# def test_save_rating_internal_error(mock_service, mock_get_db, valid_request_payload, mock_db):
#     mock_get_db.return_value = mock_db
#     mock_db.query.return_value.filter.return_value.first.return_value = AppraisalCycle(cycle_id=1, status="active")
#     mock_service.side_effect = Exception("Unexpected error")

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
#     assert response.json()["detail"] == "Internal server error."


# import pytest
# from fastapi.testclient import TestClient
# from fastapi import status
# from unittest.mock import patch, MagicMock
# import sys
# import os

# # Add project root to sys.path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from main import app
# from models.appraisal_cycle import AppraisalCycle

# client = TestClient(app)

# # Test payload
# @pytest.fixture
# def valid_request_payload():
#     return {
#         "cycle_id": 1,
#         "employee_id": 1001,
#         "ratings": [
#             {"parameter_id": 1, "parameter_rating": 4},
#             {"parameter_id": 2, "parameter_rating": 5}
#         ],
#         "discussion_date": "2024-05-01"
#     }

# # Helper function to mock AppraisalCycle DB query
# def mock_cycle_query(status="active"):
#     cycle = AppraisalCycle(cycle_id=1, status=status)
#     query_mock = MagicMock()
#     query_mock.filter.return_value.first.return_value = cycle
#     return query_mock

# # === TEST CASES ===

# @patch("routes.lead_assessment.get_db")
# @patch("services.lead_assessment.save_lead_assessment_rating_service")
# def test_save_rating_success(mock_service, mock_get_db, valid_request_payload):
#     mock_db = MagicMock()
#     mock_db.query.return_value = mock_cycle_query(status="active")
#     mock_get_db.return_value = mock_db

#     mock_service.return_value = {"message": "Ratings saved successfully"}

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == {"message": "Ratings saved successfully"}


# @patch("routes.lead_assessment.get_db")
# def test_save_rating_inactive_cycle(mock_get_db, valid_request_payload):
#     mock_db = MagicMock()
#     mock_db.query.return_value = mock_cycle_query(status="completed")
#     mock_get_db.return_value = mock_db

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.json()["detail"] == "The selected appraisal cycle is not active."


# @patch("routes.lead_assessment.get_db")
# @patch("services.lead_assessment.save_lead_assessment_rating_service")
# def test_save_rating_no_allocation(mock_service, mock_get_db, valid_request_payload):
#     mock_db = MagicMock()
#     mock_db.query.return_value = mock_cycle_query(status="active")
#     mock_get_db.return_value = mock_db

#     mock_service.side_effect = ValueError("No allocation found")

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     assert response.json()["detail"] == "No allocation found for the selected cycle and employee."


# @patch("routes.lead_assessment.get_db")
# @patch("services.lead_assessment.save_lead_assessment_rating_service")
# def test_save_rating_internal_error(mock_service, mock_get_db, valid_request_payload):
#     mock_db = MagicMock()
#     mock_db.query.return_value = mock_cycle_query(status="active")
#     mock_get_db.return_value = mock_db

#     mock_service.side_effect = Exception("Unexpected DB error")

#     response = client.post("/lead_assessment/save_rating", json=valid_request_payload)

#     assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
#     assert response.json()["detail"] == "Internal server error."
