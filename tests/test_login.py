# import pytest
# from fastapi.testclient import TestClient
# from fastapi import status

# # from database.connection import get_db  # the original get_db dependency
# from sqlalchemy.orm import Session
# from unittest.mock import MagicMock
# # from routers.auth import authenticate_employee  # or however you import it

# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from main import app

# client = TestClient(app)


# # Mock DB session
# @pytest.fixture
# def mock_db():
#     db = MagicMock(spec=Session)
#     return db

# # Successful login test
# def test_login_success(monkeypatch, mock_db):
#     # Mock the authenticate_employee function to return a fake employee
#     class FakeEmployee:
#         employee_id = "Emp01"
#         role = "employee"
#         password = "1234"

#     def mock_authenticate_employee(db, employee_id, password):
#         return FakeEmployee()

#     monkeypatch.setattr("routes.login.authenticate_employee", mock_authenticate_employee)
#     monkeypatch.setattr("routes.login.get_db", lambda: mock_db)

#     response = client.post("/auth/login", json={"employee_id": "Emp01", "password": "1234"})

#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == {
#         "message": "Login successful",
#         "employee_id": "Emp01",
#         "role": "employee",
#     }

# # Failed login test
# def test_login_failure(monkeypatch, mock_db):
#     def mock_authenticate_employee(db, employee_id, password):
#         return None

#     monkeypatch.setattr("routes.login.authenticate_employee", mock_authenticate_employee)
#     monkeypatch.setattr("routes.login.get_db", lambda: mock_db)

#     response = client.post("/auth/login", json={"employee_id": "Emp02", "password": "12344"})

#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#     assert response.json() == {"detail": "Invalid credentials"}


import pytest
from fastapi.testclient import TestClient
from fastapi import status
import sys
import os
from unittest.mock import MagicMock
from sqlalchemy.exc import SQLAlchemyError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

client = TestClient(app)


# Mocking database session
@pytest.fixture
def mock_db():
    return MagicMock()


def test_successful_login(mock_db):
    # Mock the authenticate_employee function to return a valid employee
    mock_employee = MagicMock()
    mock_employee.id = "Emp01"
    mock_employee.role = "employee"
    mock_employee.password = "1234"

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "routes.login.authenticate_employee", lambda db, emp_id, pwd: mock_employee
        )

        response = client.post(
            "/auth/login", json={"employee_id": "Emp01", "password": "1234"}
        )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Login successful",
        "employee_id": "Emp01",
        "role": "employee",
    }


def test_invalid_credentials(mock_db):
    # Mock authenticate_employee to return None for invalid credentials
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("routes.login.authenticate_employee", lambda db, emp_id, pwd: None)

        response = client.post(
            "/auth/login", json={"employee_id": "Emp01", "password": "wewe"}
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_database_error(mock_db):
    # Simulate a database exception (SQLAlchemyError)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "routes.login.authenticate_employee",
            lambda db, emp_id, pwd: (_ for _ in ()).throw(
                SQLAlchemyError("Database error")
            ),
        )

        response = client.post(
            "/auth/login", json={"employee_id": "Emp01", "password": "1234"}
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "Database error occurred"}


def test_unexpected_error(mock_db):
    # Simulate an unexpected exception during the login process
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "routes.login.authenticate_employee",
            lambda db, emp_id, pwd: (_ for _ in ()).throw(
                Exception("Unexpected error")
            ),
        )

        response = client.post(
            "/auth/login", json={"employee_id": "Emp01", "password": "1234"}
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "An unexpected error occurred"}
