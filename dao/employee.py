from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import SQLAlchemyError
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
            .filter((Employee.manager_id == manager_id) | (Employee.id == manager_id))
            .all()
        )
    except SQLAlchemyError as e:
        raise Exception(
            f"Database error occurred while fetching employees under manager {manager_id}: {str(e)}"
        )


# Fetch employees by employee ID
def get_employee_by_id(db: Session, employee_id: int):
    try:
        return db.query(Employee).filter(Employee.id == employee_id).first()
    except SQLAlchemyError as e:
        raise Exception(
            f"Database error while fetching employee {employee_id}: {str(e)}"
        )


# Fetch employees by reporting manager ID
def get_employee_manager(db: Session, manager_id: int):
    try:
        return db.query(Employee).filter(Employee.id == manager_id).first()
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
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return None
        return employee
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
                Employee.id == EmployeeAllocation.employee_id,
            )
            .filter(
                EmployeeAllocation.cycle_id == cycle_id,
                Employee.manager_id == team_lead_id,
            )
            .all()
        )

        team_lead = db.query(Employee).filter(Employee.id == team_lead_id).first()

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
                Employee.id,
                Employee.full_name,
                Employee.email,
                manager.full_name.label("reporting_manager_name"),
                prev_manager.full_name.label("previous_reporting_manager_name"),
            )
            .outerjoin(manager, Employee.manager_id == manager.id)
            .outerjoin(
                prev_manager,
                Employee.previous_manager_id == prev_manager.id,
            )
            .order_by(Employee.id)
            .all()
        )

        return result
    except SQLAlchemyError as e:
        raise Exception(
            f"Database error occurred while fetching sorted employees: {str(e)}"
        )


# To get employee by role id
def get_employee_by_email(db: Session, email: str):
    return db.query(Employee).filter(Employee.email == email).first()
