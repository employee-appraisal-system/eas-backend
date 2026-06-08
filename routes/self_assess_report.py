from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.connection import get_db
from dao.temp_self_assess_repo import get_response
from logger_config import logging

from services.auth_middleware import get_current_user, require_roles

router = APIRouter(
    prefix="/self_assess_report",
    tags=["Self Assessment Report"],
    dependencies=[Depends(get_current_user), Depends(require_roles("hr", "admin"))],
)


# Fetch self-assessment report for a specific cycle
@router.get("/self-assessment-report/{cycle_id}")
def get_active_cycle(cycle_id: int, db: Session = Depends(get_db)):
    """
    Retrieve self-assessment responses for a specific cycle

    """
    try:
             
        responses = get_response(db, cycle_id)
        logging.info(
            f"Successfully retrieved {len(responses)} self-assessment responses for cycle {cycle_id}"
        )
        return responses

    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        logging.error(
            f"Database error retrieving self-assessment report for cycle {cycle_id}: {str(db_err)}"
        )
        raise HTTPException(
            status_code=500,
            detail="Database error while retrieving self-assessment report",
        )
    except Exception as e:
        logging.error(
            f"Unexpected error retrieving self-assessment report for cycle {cycle_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving self-assessment report",
        )
