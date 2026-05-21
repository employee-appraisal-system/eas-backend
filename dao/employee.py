from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from models.employee import Employee
from models.employee_allocation import EmployeeAllocation


# Fetch all employees
def fetch_all_employees(db: Session):
    """
    Fetch all employees from the database.
    Args:
        db: Database session
    Returns:
        List of Employee objects
    """
    try:
        employees_list = db.query(Employee).all()
        return employees_list
    except SQLAlchemyError as e:
        raise Exception(
            f"Database error occurred while fetching all employees: {str(e)}"
        )


# Fetch employees by reporting manager ID ALONG WITH the employee ID
def get_employees_under_manager(db: Session, manager_id: int):
    try:
        return (
            db.query(Employee)
            .filter(
                (Employee.reporting_manager == manager_id)
                | (Employee.employee_id == manager_id)
            )
            .all()
        )
    except SQLAlchemyError as e:
        raise Exception(
            f"Database error occurred while fetching employees under manager {manager_id}: {str(e)}"
        )


# Fetch employees by employee ID
def get_employee_by_id(db: Session, employee_id: int):
    try:
        return db.query(Employee).filter(Employee.employee_id == employee_id).first()
    except SQLAlchemyError as e:
        raise Exception(
            f"Database error while fetching employee {employee_id}: {str(e)}"
        )


# Fetch employees by reporting manager ID
def get_employee_manager(db: Session, manager_id: int):
    try:
        return db.query(Employee).filter(Employee.employee_id == manager_id).first()
    except SQLAlchemyError as e:
        raise Exception(f"Database error while fetching manager {manager_id}: {str(e)}")


# get employee details by employee ID
def get_employee_details(db: Session, employee_id: int):
    """
    Fetch employee details by employee ID.
    Args:
        db: Database session
        employee_id: ID of the employee
    Returns:
        Dictionary containing employee details
    """
    try:
        employee = (
            db.query(Employee).filter(Employee.employee_id == employee_id).first()
        )
        if not employee:
            return None
        return {"role": employee.role}
    except SQLAlchemyError as e:
        raise Exception(
            f"Database error occurred while fetching employee details for {employee_id}: {str(e)}"
        )


def get_employees_under_team_lead(db: Session, cycle_id: int, team_lead_id: int):
    try:
        employees = (
            db.query(Employee)
            .join(
                EmployeeAllocation,
                Employee.employee_id == EmployeeAllocation.employee_id,
            )
            .filter(
                EmployeeAllocation.cycle_id == cycle_id,
                Employee.reporting_manager == team_lead_id,
            )
            .all()
        )

        team_lead = (
            db.query(Employee).filter(Employee.employee_id == team_lead_id).first()
        )

        if team_lead and team_lead not in employees:
            employees.append(team_lead)

        return employees
    except SQLAlchemyError as e:
        raise Exception(
            f"Database error occurred while fetching employees under team lead {team_lead_id} for cycle {cycle_id}: {str(e)}"
        )


def get_all_employees_sorted(db: Session):
    try:
        manager = aliased(Employee)
        prev_manager = aliased(Employee)

        result = (
            db.query(
                Employee.employee_id,
                Employee.employee_name,
                Employee.role,
                manager.employee_name.label("reporting_manager_name"),
                prev_manager.employee_name.label("previous_reporting_manager_name"),
            )
            .outerjoin(manager, Employee.reporting_manager == manager.employee_id)
            .outerjoin(
                prev_manager,
                Employee.previous_reporting_manager == prev_manager.employee_id,
            )
            .order_by(Employee.employee_id)
            .all()
        )

        return result
    except SQLAlchemyError as e:
        raise Exception(
            f"Database error occurred while fetching sorted employees: {str(e)}"
        )


# To get employee by role id
def get_employee_by_role_id(db: Session, role_id: str):
    return db.query(Employee).filter(Employee.role_id == role_id).first()
