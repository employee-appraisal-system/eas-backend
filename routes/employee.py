from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from database.connection import get_db
from services.employee import (
    get_all_employees,
    get_sorted_employees,
    fetch_employees_under_manager,
    fetch_reporting_manager,
    fetch_employee_details,
    fetch_employees_under_team_lead,
)
from schema.employee import EmployeeResponse, EmployeeRoleResponse
from models.employee import Employee
from services.auth_middleware import (
    get_current_user,
    require_roles,
    require_self_or_roles,
)

router = APIRouter(
    prefix="/employee", tags=["Employee"], dependencies=[Depends(get_current_user)]
)


# Get all employees
@router.get("/")
def read_employees_list(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_roles("hr", "admin")),
):
    """
    Fetch all employees (Protected Route)
    """

    try:
        return get_all_employees(db)

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Database error occurred while fetching employees."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get employees under a specific manager


@router.get("/reporting/{manager_id}")
def get_reporting_employees(
    manager_id: int,
    db: Session = Depends(get_db),
    _role_user: dict = Depends(require_roles("team lead", "hr", "admin")),
    _scope_user: dict = Depends(require_self_or_roles("manager_id", "hr", "admin")),
):
    try:
        employees = fetch_employees_under_manager(db, manager_id)
        if not employees:
            raise HTTPException(
                status_code=404, detail="No employees found under this manager"
            )
        return employees
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching employees under manager.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get employees under a team lead
@router.get("/reporting_manager/{employee_id}")
def get_reporting_manager(
    employee_id: int,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_self_or_roles("employee_id", "hr", "admin", "team lead")),
):
    """
    fetch the reporting manager for a given employee
    Args:
        employee_id: ID of the employee
        db: Database session
    Returns:
        Dictionary containing reporting manager ID and name
    """
    try:
        result, error = fetch_reporting_manager(db, employee_id)
        if error == "Employee not found":
            raise HTTPException(status_code=404, detail=error)
        elif error in ["No manager assigned", "Manager not found"]:
            return {"reporting_manager_id": None, "reporting_manager_name": error}
        return result
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching reporting manager.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get employee details by ID
@router.get("/employee_details/{employee_id}", response_model=EmployeeRoleResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_self_or_roles("employee_id", "hr", "admin", "team lead")),
):
    try:
        employee, error = fetch_employee_details(db, employee_id)
        if error == "Employee not found":
            raise HTTPException(status_code=404, detail=error)
        return employee
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching employee details.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get employees for a specific appraisal cycle under a team lead
@router.get("/employees/{cycle_id}/{team_lead_id}")
def get_employees_for_cycle(
    cycle_id: int,
    team_lead_id: int,
    db: Session = Depends(get_db),
    _role_user: dict = Depends(require_roles("team lead", "hr", "admin")),
    _scope_user: dict = Depends(require_self_or_roles("team_lead_id", "hr", "admin")),
):
    try:
        employees, error = fetch_employees_under_team_lead(db, cycle_id, team_lead_id)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return employees
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching employees for cycle.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Historical report: get all employees in sorted manner
@router.get("/employees", response_model=List[EmployeeResponse])
def get_all_sorted_employees(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_roles("hr", "admin")),
):
    try:
        return get_sorted_employees(db)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching sorted employees.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
