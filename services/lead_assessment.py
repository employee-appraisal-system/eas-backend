from sqlalchemy.orm import Session
from dao.lead_assessment import (
    get_overall_performance_rating,
    save_lead_assessment_rating,
)
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError


# To save the lead assessment ratings
def save_lead_assessment_rating_service(
    db: Session, cycle_id: int, employee_id: int, ratings: list, discussion_date
):
    try:
        result = save_lead_assessment_rating(
            db=db,
            cycle_id=cycle_id,
            employee_id=employee_id,
            ratings=ratings,
            discussion_date=discussion_date,
        )
        return result
    except ValueError as valueException:
        raise HTTPException(status_code=400, detail=str(valueException))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


# Fetch only rating for fixed parameter - 'Overall Performance Rating'
def get_overall_rating_of_employee(db: Session, cycle_id: int):
    try:
        return get_overall_performance_rating(db, cycle_id)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while retrieving employee ratings.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error")
