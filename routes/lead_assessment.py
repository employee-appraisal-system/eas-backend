from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from schema.lead_assessment import (
    LeadAssessmentRatingRequest,
    LeadAssessmentRatingResponse,
)
from services.lead_assessment import (
    save_lead_assessment_rating_service,
    get_overall_rating_of_employee,
)
from models.lead_assessment import LeadAssessmentRating
from models.appraisal_cycle import AppraisalCycle
from database.connection import get_db
from services.auth_middleware import (
    get_current_user,
    normalize_role,
    require_roles,
)

from dao.employee import get_employees_under_team_lead

router = APIRouter(
    prefix="/lead_assessment",
    tags=["Lead Assessment"],
    dependencies=[Depends(get_current_user)],
)


# Save lead assessment ratings
@router.post("/save_rating")
def save_rating(
    request: LeadAssessmentRatingRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
    _role_user: dict = Depends(require_roles("team lead", "hr", "admin")),
):
    """
    Save lead assessment ratings.
    Args:
        request: LeadAssessmentRatingRequest object containing cycle_id, employee_id, ratings, and discussion_date
        db: Database session
    Returns:
        Result of the save operation"""
    try:
        user_role = normalize_role(user.get("role"))
        is_privileged = user_role in {normalize_role("hr"), normalize_role("admin")}

        if not is_privileged:
            token_employee_id = user.get("employee_id")
            if token_employee_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")

            if str(request.employee_id) == str(token_employee_id):
                raise HTTPException(
                    status_code=403,
                    detail="Forbidden",
                )

            allowed_employees = get_employees_under_team_lead(
                db, request.cycle_id, int(token_employee_id)
            )
            allowed_employee_ids = {e.id for e in allowed_employees}
            if request.employee_id not in allowed_employee_ids:
                raise HTTPException(status_code=403, detail="Forbidden")

        # Check if the cycle is active
        cycle = (
            db.query(AppraisalCycle)
            .filter(AppraisalCycle.cycle_id == request.cycle_id)
            .first()
        )
        if not cycle:
            raise HTTPException(status_code=404, detail="Appraisal cycle not found")

        if cycle.status.lower() != "active":
            raise HTTPException(
                status_code=400, detail="The selected appraisal cycle is not active."
            )

        result = save_lead_assessment_rating_service(
            db,
            cycle_id=request.cycle_id,
            employee_id=request.employee_id,
            ratings=request.ratings,
            discussion_date=request.discussion_date,
        )
        return result

    except ValueError as ve:
        # Handle specific cases for allocation errors or other validation errors
        if "Employee is not allocated to this cycle" in str(ve):
            raise HTTPException(
                status_code=404,
                detail="No allocation found for the selected cycle and employee.",
            )
        elif "discussion date" in str(ve):  # Check for date parsing errors
            raise HTTPException(
                status_code=400, detail=str(ve)
            )  # Bad request for invalid date
        raise HTTPException(status_code=400, detail=str(ve))

    except HTTPException as he:
        # Re-raise HTTPException without overwriting
        raise he

    except Exception as e:
        print("Unexpected error:", e)
        raise HTTPException(status_code=500, detail="Internal server error.")


# Fetch previous ratings for a given employee and cycle
@router.get("/lead_assessment/previous_data/{cycle_id}/{employee_id}")
def get_previous_ratings(
    cycle_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
    _role_user: dict = Depends(require_roles("team lead", "hr", "admin")),
):
    """
    Fetch previous ratings for a given employee and cycle.
    Args:
        cycle_id: appraisal cycle  ID
        employee_id: employee ID
        db: Database session
    Returns:
        Dictionary containing cycle status, ratings, and discussion date"""
    try:
        user_role = normalize_role(user.get("role"))
        is_privileged = user_role in {normalize_role("hr"), normalize_role("admin")}

        if not is_privileged:
            token_employee_id = user.get("employee_id")
            if token_employee_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")

            allowed_employees = get_employees_under_team_lead(
                db, cycle_id, int(token_employee_id)
            )
            allowed_employee_ids = {e.id for e in allowed_employees}
            if employee_id not in allowed_employee_ids:
                raise HTTPException(status_code=403, detail="Forbidden")

        # Fetch cycle status
        cycle = (
            db.query(AppraisalCycle).filter(AppraisalCycle.cycle_id == cycle_id).first()
        )
        if not cycle:
            raise HTTPException(status_code=404, detail="Appraisal cycle not found")

        # Fetch previous ratings for the given employee and cycle
        previous_ratings = (
            db.query(LeadAssessmentRating)
            .filter(
                LeadAssessmentRating.cycle_id == cycle_id,
                LeadAssessmentRating.employee_id == employee_id,
            )
            .all()
        )

        return {
            "cycle_status": cycle.status,
            "ratings": [
                {
                    "parameter_id": r.parameter_id,
                    "parameter_rating": r.parameter_rating,
                    "specific_input": r.specific_input,
                }
                for r in previous_ratings
            ],
            "discussion_date": (
                previous_ratings[0].discussion_date if previous_ratings else None
            ),
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        # Catch any unexpected exceptions
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# historic report


# For getting list of employee_id and "overall performance rating" for a selected cycle
@router.get(
    "/employees_ratings/{cycle_id}", response_model=list[LeadAssessmentRatingResponse]
)
def get_employee_ratings(
    cycle_id: int,
    db: Session = Depends(get_db),
    _user: dict = Depends(require_roles("hr", "admin")),
):
    """
    Get list of employee_id and "overall performance rating" for a selected cycle.
    Args:
        cycle_id: appraisal cycle ID
        db: Database session
    Returns:
        List of LeadAssessmentRatingResponse objects containing employee_id and parameter_rating
    """
    try:
        data = get_overall_rating_of_employee(db, cycle_id)       
        return data

    except SQLAlchemyError as exception:
        raise HTTPException(
            status_code=500, detail="Database error occurred while fetching ratings."
        )
    except Exception as exception:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(exception)}"
        )
