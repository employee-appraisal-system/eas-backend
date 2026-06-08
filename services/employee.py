from sqlalchemy.orm import Session
from fastapi import HTTPException
from dao.employee import (
    fetch_all_employees,
    get_all_employees_sorted,
    get_employees_under_manager,
    get_employee_by_id,
    get_employee_manager,
    get_employee_details,
    get_employees_under_team_lead,
)
from services.role_mapping import get_entra_roles_for_user


def _resolve_employee_role(email: str | None) -> str:
    if not email:
        return ""
    return ", ".join(get_entra_roles_for_user(email))


def _serialize_employee(employee):
    return {
        "id": employee.id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "full_name": employee.full_name,
        "email": employee.email,
        "role": _resolve_employee_role(employee.email),
        "manager_id": employee.manager_id,
        "previous_manager_id": employee.previous_manager_id,
    }


def _serialize_employee_row(employee_row):
    return {
        "id": employee_row.id,
        "full_name": employee_row.full_name,
        "role": _resolve_employee_role(employee_row.email),
        "reporting_manager_name": employee_row.reporting_manager_name,
        "previous_reporting_manager_name": employee_row.previous_reporting_manager_name,
    }


# Get list of all employees
def get_all_employees(db: Session):
    try:
        return [_serialize_employee(employee) for employee in fetch_all_employees(db)]
    except HTTPException:
        raise


# Get sorted list of all employees
def get_sorted_employees(db: Session):
    try:
        return [_serialize_employee_row(employee) for employee in get_all_employees_sorted(db)]
    except HTTPException:
        raise


# Get the list of employees under the particular team lead
def fetch_employees_under_manager(db: Session, manager_id: int):
    try:
        employees = get_employees_under_manager(db, manager_id)
        return [_serialize_employee(employee) for employee in employees]
    except Exception as e:
        raise e


# Get the reporting manager of the employee
def fetch_reporting_manager(db: Session, employee_id: int):
    try:
        employee = get_employee_by_id(db, employee_id)
        if not employee:
            return None, "Employee not found"

        if not employee.manager_id:
            return None, "No manager assigned"

        manager = get_employee_manager(db, employee.manager_id)
        if not manager:
            return None, "Manager not found"

        return {
            "reporting_manager_id": manager.id,
            "reporting_manager_name": manager.full_name,
        }, None
    except Exception as e:
        raise e


# Get the details of the employee
def fetch_employee_details(db: Session, employee_id: int):
    try:
        employee_data = get_employee_details(db, employee_id)
        if not employee_data:
            return None, "Employee not found"
        return {"role": _resolve_employee_role(employee_data.email)}, None
    except Exception as e:
        raise e


# Get the list of employees under the particular team lead
def fetch_employees_under_team_lead(db: Session, cycle_id: int, team_lead_id: int):
    try:
        employees = get_employees_under_team_lead(db, cycle_id, team_lead_id)
        if not employees:
            return None, "No employees found for this cycle."
        return [_serialize_employee(employee) for employee in employees], None
    except Exception as e:
        raise e
