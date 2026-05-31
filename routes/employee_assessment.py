from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List

from database.connection import get_db
from schema.employee_assessment import (
    AssessmentResponseIn,
    AssessmentResponseOut,
    QuestionOut,
)
from services.employee_assessment import (
    get_employee_cycles,
    get_questions_for_cycle,
    save_self_assessment_responses,
    get_readonly_responses,
)
from dao.employee_assessment import get_team_lead_cycles
from services.auth_middleware import get_current_user

router = APIRouter(prefix="/employee_assessment", tags=["Self Assessment"], dependencies=[Depends(get_current_user)]
)


# Fetch the active and completed cycles for which employee is allocated
@router.get("/cycles/{employee_id}")
def fetch_employee_cycles(employee_id: int, db: Session = Depends(get_db)):
    """
    Fetch the active and completed cycles for which employee is allocated.
    Args:
        employee_id: ID of the employee
        db: Database session
    Returns:
        List of AppraisalCycle objects
    """
    try:
        cycles = get_employee_cycles(db, employee_id)
        return cycles
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching employee cycles.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teamlead/cycles/{team_lead_id}")
def fetch_team_lead_cycles(team_lead_id: int, db: Session = Depends(get_db)):
    cycles = get_team_lead_cycles(db, team_lead_id)
    if not cycles:
        raise HTTPException(
            status_code=404, detail="No appraisal cycles found for team lead."
        )
    return cycles


# Fetch questions assigned to the employee for active and completed cycles
@router.get("/questions/{employee_id}/{cycle_id}", response_model=List[QuestionOut])
def fetch_questions(employee_id: int, cycle_id: int, db: Session = Depends(get_db)):
    try:
        questions = get_questions_for_cycle(db, employee_id, cycle_id)
        if not questions:
            raise HTTPException(status_code=404, detail="No questions found.")
        return questions
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Database error occurred while fetching questions."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add response and submit
@router.post("/submit", response_model=dict)
def submit_assessment(
    responses: List[AssessmentResponseIn], db: Session = Depends(get_db)
):
    try:
        if not responses:
            raise HTTPException(status_code=400, detail="No responses submitted.")
        return save_self_assessment_responses(db, responses)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while submitting responses.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


#  Fetch the responses
@router.get(
    "/responses/{employee_id}/{cycle_id}", response_model=List[AssessmentResponseOut]
)
def view_responses(employee_id: int, cycle_id: int, db: Session = Depends(get_db)):
    responses = get_readonly_responses(db, employee_id, cycle_id)
    if not responses:
        raise HTTPException(status_code=404, detail="No responses found.")
    return responses
