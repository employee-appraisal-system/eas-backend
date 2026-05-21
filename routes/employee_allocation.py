from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.connection import get_db
from models.employee_allocation import EmployeeAllocation
from typing import List

router = APIRouter(prefix="/employee-allocation", tags=["Employee Allocation"])


# get all employees allocated to a specific cycle
@router.get("/{cycle_id}", response_model=List[int])
def get_allocated_employees(cycle_id: int, db: Session = Depends(get_db)):
    """
    Fetch all employees allocated to a specific appraisal cycle.
    Args:
        cycle_id: ID of the appraisal cycle
        db: Database session
    Returns:
        List of employee IDs allocated to the cycle
    """
    try:
        employees = (
            db.query(EmployeeAllocation.employee_id)
            .filter(EmployeeAllocation.cycle_id == cycle_id)
            .all()
        )

        if not employees:
            raise HTTPException(
                status_code=404, detail="No employees allocated to this cycle."
            )

        return [emp.employee_id for emp in employees]

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
