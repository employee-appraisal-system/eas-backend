from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from models.employee_allocation import EmployeeAllocation
from models.assignment import QuestionAssignment
from models.questions import Question
from models.self_assessment_response import SelfAssessmentResponse
from models.appraisal_cycle import AppraisalCycle
from models.stages import Stage
from models.employee import Employee
from sqlalchemy import or_, and_
from typing import List


# Get the cycle status
def get_cycle_status(db: Session, cycle_id: int) -> str:
    """
    Fetch the status of a specific appraisal cycle.
    Args:
        db: Database session
        cycle_id: appraisal cycle ID
    Returns:
        Status of the cycle
    """
    try:
        cycle = (
            db.query(AppraisalCycle).filter(AppraisalCycle.cycle_id == cycle_id).first()
        )
        return cycle.status if cycle else None
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Database error while fetching cycle status."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Fetch the active and completed cycles for which employee is allocated
def get_allocated_cycles(db: Session, employee_id: int):
    """
    Fetch the active and completed cycles for which the employee is allocated.
    Args:
        db: Database session
        employee_id: ID of the employee
    Returns:
        List of AppraisalCycle objects
    """
    try:
        return (
            db.query(AppraisalCycle)
            .join(EmployeeAllocation)
            .join(Stage)
            .filter(
                EmployeeAllocation.employee_id == employee_id,
                or_(
                    AppraisalCycle.status == "completed",
                    and_(
                        AppraisalCycle.status == "active",
                        Stage.stage_name == "Self Assessment",
                        or_(Stage.is_active == True, Stage.is_completed == True),
                    ),
                ),
            )
            .all()
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Database error while fetching allocated cycles."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Fetch the active (for which self assessment stage is either active or completed)  and completed cycles  for which either the team lead or one of the employee under him is allocated
def get_team_lead_cycles(db: Session, team_lead_id: int):
    """
    Fetch the active and completed cycles for which either the team lead or one of the employees under him is allocated.
    Args:
        db: Database session
        team_lead_id: ID of the team lead
    Returns:
        List of AppraisalCycle objects"""
    # Step 1: Find all employees reporting to this team lead (including the team lead themselves)
    employee_ids = (
        db.query(Employee.id)
        .filter(
            or_(
                Employee.manager_id == team_lead_id,
                Employee.id == team_lead_id,
            )
        )
        .all()
    )

    # 'employee_ids' will be a list of tuples like [(1,), (2,), (3,)]
    employee_ids = [emp_id for (emp_id,) in employee_ids]

    # Step 2: Fetch all cycles that are either completed or active for which the "Self Assessment" stage is either active or completed
    cycles = (
        db.query(AppraisalCycle)
        .join(EmployeeAllocation)
        .join(Stage)
        .filter(
            EmployeeAllocation.employee_id.in_(
                employee_ids
            ),  # Allocation to any of the employee_ids
            or_(
                AppraisalCycle.status == "completed",  # Completed cycles
                and_(
                    AppraisalCycle.status == "active",  # Active cycles
                    Stage.stage_name == "Self Assessment",  # Only Self Assessment stage
                    or_(Stage.is_active == True, Stage.is_completed == True),
                ),
            ),
        )
        .all()
    )

    return cycles


# Fetch questions assigned to the employee for the selected active and completed cycles
def get_assigned_questions_with_options(db: Session, employee_id: int, cycle_id: int):
    """
    Fetch questions assigned to the employee for the selected active and completed cycles.
    Args:
        db: Database session
        employee_id: ID of the employee
        cycle_id: appraisal cycle ID
    Returns:
        List of Question objects with their options
    """
    try:
        allocation = (
            db.query(EmployeeAllocation)
            .filter_by(employee_id=employee_id, cycle_id=cycle_id)
            .first()
        )
        allocation_id = allocation.allocation_id if allocation else None

        questions = (
            db.query(Question)
            .join(QuestionAssignment)
            .options(joinedload(Question.options))
            .filter(
                QuestionAssignment.employee_id == employee_id,
                QuestionAssignment.cycle_id == cycle_id,
            )
            .all()
        )

        for question in questions:
            question.allocation_id = allocation_id

        return questions
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Database error while fetching assigned questions."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Fetch the existing responses for the employee and cycle
def get_existing_responses(db: Session, employee_id: int, cycle_id: int):
    try:
        return (
            db.query(SelfAssessmentResponse)
            .options(
                joinedload(SelfAssessmentResponse.question),
                joinedload(SelfAssessmentResponse.option),
            )
            .filter(
                SelfAssessmentResponse.employee_id == employee_id,
                SelfAssessmentResponse.cycle_id == cycle_id,
            )
            .all()
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Database error while fetching existing responses."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Save self assessment responses for the active cycles
def submit_self_assessment_responses(
    db: Session, responses: List[SelfAssessmentResponse]
):
    """
    Save self-assessment responses for the active cycles.
    Args:
        db: Database session
        responses: List of SelfAssessmentResponse objects to save
    """
    try:
        db.add_all(responses)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Database error while saving responses."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
