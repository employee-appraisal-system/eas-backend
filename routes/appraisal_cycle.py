from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from services.appraisal_cycle import (
    add_new_cycle,
    fetch_all_cycles,
    fetch_cycle_by_id,
    fetch_all_cycles_with_stages,
    delete_appraisal_cycle,
    get_completed_cycles,
    get_filtered_cycles,
    get_cycle_status_service,
)
from schema.appraisal_cycle_pydantic import (
    AppraisalCycleCreate,
    AppraisalCycleResponse,
    AppraisalCycleResponseWithStages,
)
from database.connection import get_db
from services.auth_middleware import get_current_user

# from models.appraisal_cycle import AppraisalCycle

router = APIRouter(
    prefix="/appraisal_cycle",
    tags=["Appraisal"],
    dependencies=[Depends(get_current_user)]
)

# Create a new cycle
@router.post("/", response_model=AppraisalCycleResponse)
def create_cycle(cycle_data: AppraisalCycleCreate, db: Session = Depends(get_db)):
    """'
    Create a new appraisal cycle.
    Args:
        cycle_data: object containing cycle details
        db: Database session
    Returns:
        Newly created AppraisalCycle object

    """
    try:
        if cycle_data.status not in ["active", "inactive"]:
            raise HTTPException(
                status_code=422,
                detail="Invalid status. Allowed values: 'active', 'inactive'",
            )

        if cycle_data.end_date_of_cycle < cycle_data.start_date_of_cycle:
            raise HTTPException(
                status_code=400, detail="End date cannot be before start date."
            )

        return add_new_cycle(db, cycle_data)

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception))


# Get all cycles
@router.get("/", response_model=list[AppraisalCycleResponse])
def get_cycles(db: Session = Depends(get_db)):
    try:
        return fetch_all_cycles(db)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception))


# Get all cycles with stage names
@router.get("/with-stage-names", response_model=list[AppraisalCycleResponseWithStages])
def get_cycles_with_stage_names(db: Session = Depends(get_db)):
    try:
        return fetch_all_cycles_with_stages(db)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception))


# Get cycle by ID
@router.get("/{cycle_id}", response_model=AppraisalCycleResponse)
def get_cycle(cycle_id: int, db: Session = Depends(get_db)):
    try:
        cycle = fetch_cycle_by_id(db, cycle_id)
        if not cycle:
            raise HTTPException(status_code=404, detail="Cycle not found")
        return cycle
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception))


# Delete cycle by ID
@router.delete("/{cycle_id}")
def delete_cycle(cycle_id: int, db: Session = Depends(get_db)):
    try:
        return delete_appraisal_cycle(db, cycle_id)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception))


# Get status of appraisal cycles
@router.get("/status/{cycle_id}")
def get_appraisal_cycle_status(cycle_id: int, db: Session = Depends(get_db)):
    try:
        return get_cycle_status_service(db, cycle_id)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception))


# Historical report
@router.get(
    "/appraisal-cycles/historic-report", response_model=list[AppraisalCycleResponse]
)
def get_cycles_for_historic_report(db: Session = Depends(get_db)):
    try:
        return get_completed_cycles(db)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception))


# Self-assessment report
@router.get(
    "/appraisal-cycles/self-assessment-report",
    response_model=list[AppraisalCycleResponse],
)
def get_cycles_for_self_assessment_report(db: Session = Depends(get_db)):
    try:
        return get_filtered_cycles(db)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception))
