from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.connection import get_db
from dao.temp_self_assess_repo import get_response
from schema.edit_appraisal_cycle import GetAppraisalCycleResponse
from models.appraisal_cycle import AppraisalCycle
from logger_config import logging
from typing import List, Dict

router = APIRouter(tags=["Self Assessment Report"])


# Fetch self-assessment report for a specific cycle
@router.get("/self-assessment-report/{cycle_id}")
def get_active_cycle(cycle_id: int, db: Session = Depends(get_db)):
    """
    Retrieve self-assessment responses for a specific cycle

    """
    try:
        cycle = (
            db.query(AppraisalCycle).filter(AppraisalCycle.cycle_id == cycle_id).first()
        )
        if not cycle:
            logging.warning(
                f"Attempt to retrieve self-assessment report for non-existent cycle {cycle_id}"
            )
            raise HTTPException(
                status_code=404, detail=f"Appraisal cycle with ID {cycle_id} not found"
            )

        logging.info(f"Fetching self-assessment report for cycle {cycle_id}")

        responses = get_response(db, cycle_id)

        if not responses:
            logging.warning(f"No self-assessment responses found for cycle {cycle_id}")
            raise HTTPException(
                status_code=404,
                detail=f"No self-assessment responses found for cycle {cycle_id}",
            )

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
