from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from dao.edit_appraisal_cycle import get_cycle, edit_cycle

# update_appraisal_cycle
from schema.edit_appraisal_cycle import GetAppraisalCycleResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
from models.edit_appraisal_cycle import CycleUpdate

from logger_config import logging

from services.auth_middleware import get_current_user, require_roles

router = APIRouter(
    prefix="/edit-appraisal-cycle",
    tags=["Edit Appraisal Cycle"],
    dependencies=[Depends(get_current_user), Depends(require_roles("hr", "admin"))],
)


@router.get("/edit-appraisal-cycle/{cycle_id}")
def get_appraisal_cycle(cycle_id: int, db: Session = Depends(get_db)):
    """
    Get an appraisal cycle by its ID
    """
    try:
        logging.info(f"Incoming request to get appraisal cycle with ID {cycle_id}")
        cycle = get_cycle(db, cycle_id)
        logging.info(f"Successfully retrieved cycle with ID {cycle_id}")
        return cycle
    except HTTPException as http_err:
        logging.error(f"HTTP error for cycle with ID {cycle_id}: {http_err.detail}")
        raise
    except SQLAlchemyError as db_err:
        logging.error(
            f"Database error while retrieving cycle with ID {cycle_id}: {str(db_err)}"
        )
        raise HTTPException(
            status_code=500, detail="Database error while retrieving appraisal cycle"
        )
    except Exception as e:
        logging.error(f"Unexpected error retrieving cycle with ID {cycle_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving appraisal cycle",
        )


@router.put("/edit-appraisal-cycle/{cycle_id}")
def edit_appraisal_cycle(
    cycle_id: int, cycle_data: CycleUpdate, db: Session = Depends(get_db)
):
    """
    Update an appraisal cycle by its ID
    """
    try:
        logging.info(f"Incoming request to update appraisal cycle with ID {cycle_id}")
        response = edit_cycle(db, cycle_id, cycle_data)
        logging.info(f"Successfully updated cycle with ID {cycle_id}")
        return response
    except HTTPException as http_err:
        logging.error(f"HTTP error for cycle with ID {cycle_id}: {http_err.detail}")
        raise
    except ValueError as val_err:
        logging.error(f"Validation error for cycle with ID {cycle_id}: {str(val_err)}")
        raise HTTPException(status_code=422, detail=str(val_err))
    except SQLAlchemyError as db_err:
        logging.error(
            f"Database error while updating cycle with ID {cycle_id}: {str(db_err)}"
        )
        raise HTTPException(
            status_code=500, detail="Database error while updating appraisal cycle"
        )
    except Exception as e:
        logging.error(f"Unexpected error updating cycle with ID {cycle_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while updating appraisal cycle",
        )
