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


# Get list of all employees
def get_all_employees(db: Session):
    try:
        return fetch_all_employees(db)
    except HTTPException:
        raise


# Get sorted list of all employees
def get_sorted_employees(db: Session):
    try:
        return get_all_employees_sorted(db)
    except HTTPException:
        raise


# Get the list of employees under the particular team lead
def fetch_employees_under_manager(db: Session, manager_id: int):
    try:
        employees = get_employees_under_manager(db, manager_id)
        return employees
    except Exception as e:
        raise e


# Get the reporting manager of the employee
def fetch_reporting_manager(db: Session, employee_id: int):
    try:
        employee = get_employee_by_id(db, employee_id)
        if not employee:
            return None, "Employee not found"

        if not employee.reporting_manager:
            return None, "No manager assigned"

        manager = get_employee_manager(db, employee.reporting_manager)
        if not manager:
            return None, "Manager not found"

        return {
            "reporting_manager_id": manager.employee_id,
            "reporting_manager_name": manager.employee_name,
        }, None
    except Exception as e:
        raise e


# Get the details of the employee
def fetch_employee_details(db: Session, employee_id: int):
    try:
        employee_data = get_employee_details(db, employee_id)
        if not employee_data:
            return None, "Employee not found"
        return employee_data, None
    except Exception as e:
        raise e


# Get the list of employees under the particular team lead
def fetch_employees_under_team_lead(db: Session, cycle_id: int, team_lead_id: int):
    try:
        employees = get_employees_under_team_lead(db, cycle_id, team_lead_id)
        if not employees:
            return None, "No employees found for this cycle."
        return employees, None
    except Exception as e:
        raise e
