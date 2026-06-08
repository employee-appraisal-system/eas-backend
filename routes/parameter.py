from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.connection import get_db
from services.parameter import (
    fetch_all_parameters,
    fetch_parameter_by_id,
    create_parameter,
)
from schema.parameter import ParameterCreate, ParameterResponse
from dao.parameter import get_parameters_for_cycle
from dao.employee import get_employee_by_id
from typing import List

from services.auth_middleware import (
    get_current_user,
    normalize_role,
    require_roles,
    require_self_or_roles,
)

router = APIRouter(
    prefix="/parameter", tags=["Parameter"], dependencies=[Depends(get_current_user)]
)


# Fetch all parameters
@router.get("/", response_model=List[ParameterResponse])
def get_parameters(
    db: Session = Depends(get_db),
    _user: dict = Depends(require_roles("hr", "admin")),
):
    try:
        return fetch_all_parameters(db)
    except HTTPException as error:
        raise error
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {str(error)}",
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(error)}",
        )


# Fetch a parameter by ID
@router.get("/{parameter_id}", response_model=ParameterResponse)
def get_parameter(
    parameter_id: int,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_roles("hr", "admin")),
):
    try:
        return fetch_parameter_by_id(db, parameter_id)
    except HTTPException as error:
        raise error
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


# Add a new parameter
@router.post("/", response_model=ParameterResponse)
def add_parameter(
    parameter_data: ParameterCreate,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_roles("hr", "admin")),
):
    try:
        return create_parameter(db, parameter_data)
    except HTTPException as error:
        raise error
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {str(error)}",
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(error)}",
        )


# Fetch appraisal cycle parameters for a given cycle based on employee role
@router.get("/{cycle_id}/{employee_id}")
def fetch_parameters(
    cycle_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    _scope_user: dict = Depends(require_self_or_roles("employee_id", "hr", "admin", "team lead")),
):
    """Fetch appraisal parameters for a given cycle and employee role"""

    # Fetch employee details
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Determine if employee is a lead
    is_lead = normalize_role(employee.role) in (normalize_role("team lead"), "lead")

    # Fetch parameters based on role
    parameters = get_parameters_for_cycle(db, cycle_id, is_lead)

    return parameters  # Return as a list, not inside an object
