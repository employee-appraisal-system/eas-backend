import os
import sys
from types import SimpleNamespace

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import employee as employee_service


def test_get_all_employees_uses_entra_role(monkeypatch):
    employees = [
        SimpleNamespace(
            id=1,
            first_name="Asha",
            last_name="Patel",
            full_name="Asha Patel",
            email="asha@example.com",
            manager_id=10,
            previous_manager_id=11,
        )
    ]

    monkeypatch.setattr(
        employee_service, "fetch_all_employees", lambda db: employees
    )
    monkeypatch.setattr(
        employee_service,
        "get_entra_roles_for_user",
        lambda email: ["Global Administrator", "Company Administrator"],
    )

    result = employee_service.get_all_employees(object())

    assert result == [
        {
            "id": 1,
            "first_name": "Asha",
            "last_name": "Patel",
            "full_name": "Asha Patel",
            "email": "asha@example.com",
            "role": "Global Administrator, Company Administrator",
            "manager_id": 10,
            "previous_manager_id": 11,
        }
    ]


def test_fetch_employee_details_uses_entra_role(monkeypatch):
    employee = SimpleNamespace(email="ravi@example.com")

    monkeypatch.setattr(
        employee_service, "get_employee_details", lambda db, employee_id: employee
    )
    monkeypatch.setattr(
        employee_service,
        "get_entra_roles_for_user",
        lambda email: ["User Administrator"],
    )

    result, error = employee_service.fetch_employee_details(object(), 7)

    assert error is None
    assert result == {"role": "User Administrator"}


def test_get_sorted_employees_uses_entra_role(monkeypatch):
    rows = [
        SimpleNamespace(
            id=3,
            full_name="Neha Rao",
            email="neha@example.com",
            reporting_manager_name="Asha Patel",
            previous_reporting_manager_name="Ravi Kumar",
        )
    ]

    monkeypatch.setattr(
        employee_service, "get_all_employees_sorted", lambda db: rows
    )
    monkeypatch.setattr(
        employee_service,
        "get_entra_roles_for_user",
        lambda email: ["Office Apps Administrator"],
    )

    result = employee_service.get_sorted_employees(object())

    assert result == [
        {
            "id": 3,
            "full_name": "Neha Rao",
            "role": "Office Apps Administrator",
            "reporting_manager_name": "Asha Patel",
            "previous_reporting_manager_name": "Ravi Kumar",
        }
    ]


def test_fetch_employees_under_team_lead_uses_entra_role(monkeypatch):
    employees = [
        SimpleNamespace(
            id=4,
            first_name="Karan",
            last_name="Mehta",
            full_name="Karan Mehta",
            email="karan@example.com",
            manager_id=3,
            previous_manager_id=None,
        )
    ]

    monkeypatch.setattr(
        employee_service,
        "get_employees_under_team_lead",
        lambda db, cycle_id, team_lead_id: employees,
    )
    monkeypatch.setattr(
        employee_service,
        "get_entra_roles_for_user",
        lambda email: ["Global Administrator"],
    )

    result, error = employee_service.fetch_employees_under_team_lead(object(), 12, 3)

    assert error is None
    assert result == [
        {
            "id": 4,
            "first_name": "Karan",
            "last_name": "Mehta",
            "full_name": "Karan Mehta",
            "email": "karan@example.com",
            "role": "Global Administrator",
            "manager_id": 3,
            "previous_manager_id": None,
        }
    ]