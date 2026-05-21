from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.assignment import (
    create_question_assignment,
    fetch_employee_assignments,
    fetch_assigned_questions,
)
from schema.assignment import AssignmentCreate, AssignmentResponse
from models.employee import Employee
from models.appraisal_cycle import AppraisalCycle
from typing import List
from models.employee_allocation import EmployeeAllocation
from logger_config import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.post("/", response_model=List[AssignmentResponse])
def assign_questions(assignment_data: AssignmentCreate, db: Session = Depends(get_db)):
    """
    Create question assignments for employees

    Args:
        assignment_data: Data for creating assignments
        db: Database session

    Returns:
        List of created assignments

    Raises:
        HTTPException: For various validation and database errors
    """
    try:
        assignments = create_question_assignment(db, assignment_data)
        return assignments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error while creating assignments"
        )


@router.get("/{employee_id}", response_model=List[AssignmentResponse])
def get_assignments(employee_id: int, db: Session = Depends(get_db)):
    """
    Retrieve assignments for a specific employee

    Args:
        employee_id: ID of the employee
        db: Database session

    Returns:
        List of assignments for the employee

    Raises:
        HTTPException: For various validation and database errors
    """
    try:
        assignments = fetch_employee_assignments(db, employee_id)

        if not assignments:
            raise HTTPException(
                status_code=404,
                detail=f"No assignments found for employee {employee_id}",
            )
        return assignments
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=500, detail="Internal server error while retrieving assignments"
        )


@router.get("/{employee_id}/{cycle_id}")
def get_assigned_questions(
    employee_id: int, cycle_id: int, db: Session = Depends(get_db)
):
    """
    Retrieve questions assigned to an employee for a specific cycle

    Args:
        employee_id: ID of the employee
        cycle_id: ID of the appraisal cycle
        db: Database session

    Returns:
        List of assigned questions

    Raise:
        HTTPException: For various validation and database errors
    """
    try:
        # Fetch assigned questions
        assigned_questions = fetch_assigned_questions(db, employee_id, cycle_id)
        return assigned_questions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving assigned questions",
        )
