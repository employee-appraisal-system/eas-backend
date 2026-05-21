import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app
from database.connection import get_db
from models.employee_allocation import EmployeeAllocation

client = TestClient(app)


# --------------------------
# Helper: Dependency override
# --------------------------
class MockQuery:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return self._result


#  Test: Successful allocation
def test_successful_allocation():
    mock_db = MagicMock()
    mock_db.query.return_value = MockQuery(
        [MagicMock(employee_id=1), MagicMock(employee_id=2)]
    )

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/employee-allocation/1")
    assert response.status_code == 200
    assert response.json() == [1, 2]

    app.dependency_overrides = {}


#  Test: No allocations
def test_no_allocation_found():
    mock_db = MagicMock()
    mock_db.query.return_value = MockQuery([])

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/employee-allocation/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "No employees allocated to this cycle."}

    app.dependency_overrides = {}


#  Test: Database error
def test_database_error():
    class ErrorQuery:
        def filter(self, *args, **kwargs):
            return self

        def all(self):
            raise SQLAlchemyError("DB connection failed")

    mock_db = MagicMock()
    mock_db.query.return_value = ErrorQuery()

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/employee-allocation/2")
    assert response.status_code == 500
    assert response.json() == {"detail": "Database error occurred"}

    app.dependency_overrides = {}


#  Test: Unexpected error
def test_unexpected_error():
    mock_db = MagicMock()

    def broken_query(*args, **kwargs):
        raise Exception("Unknown failure")

    mock_db.query.side_effect = broken_query

    app.dependency_overrides[get_db] = lambda: mock_db

    response = client.get("/employee-allocation/3")
    assert response.status_code == 500
    assert response.json() == {"detail": "An unexpected error occurred"}

    app.dependency_overrides = {}
