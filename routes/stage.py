from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database.connection import get_db
from services.stage import (
    fetch_all_stages,
    add_new_stage,
    fetch_self_assessment_stage_info,
    fetch_lead_assessment_stage_info,
)
from schema.stage import StageCreate, StageResponse, StageInfoResponse
from typing import List
from models import Stage
from models import AppraisalCycle

router = APIRouter(prefix="/stages", tags=["Stages"])


# Fetch all stages
@router.get("/", response_model=List[StageResponse])
def get_stages(db: Session = Depends(get_db)):
    try:
        stages = fetch_all_stages(db)
        if not stages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No stages found"
            )
        return stages
    except HTTPException:
        # Re-raise HTTPExceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


# Add a new stage with validation and proper exception handling
@router.post("/", response_model=StageResponse)
def create_new_stage(stage_data: StageCreate, db: Session = Depends(get_db)):
    try:
        return add_new_stage(db, stage_data)
    except Exception as exception:
        raise HTTPException(status_code=500, detail=str(exception))


# Route to get the current stage
@router.get("/current", response_model=StageResponse)
def get_current_stage(
    cycle_id: int = Query(..., description="Cycle ID to get the current stage for"),
    db: Session = Depends(get_db),
):
    try:
        # Fetch the cycle
        cycle = (
            db.query(AppraisalCycle).filter(AppraisalCycle.cycle_id == cycle_id).first()
        )
        if not cycle:
            raise HTTPException(status_code=404, detail="Cycle not found")

        # If cycle is inactive, return the "Setup" stage
        if cycle.status == "inactive":
            setup_stage = (
                db.query(Stage)
                .filter(
                    Stage.cycle_id == cycle_id,
                    Stage.stage_name.ilike("Setup"),  # case-insensitive match
                )
                .first()
            )

            if not setup_stage:
                raise HTTPException(
                    status_code=404, detail="Setup stage not found for inactive cycle"
                )

            return setup_stage

        # For active cycles, return the active stage
        current_stage = (
            db.query(Stage)
            .filter(Stage.cycle_id == cycle_id, Stage.is_active == True)
            .first()
        )

        if not current_stage:
            raise HTTPException(
                status_code=404, detail="No active stage found for the given cycle"
            )

        return current_stage

    except HTTPException:
        # Re-raise known HTTP exceptions
        raise

    except Exception as exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/self-assessment/{cycle_id}", response_model=StageInfoResponse)
def get_self_assessment_stage(cycle_id: int, db: Session = Depends(get_db)):
    try:
        return fetch_self_assessment_stage_info(cycle_id, db)
    except HTTPException:
        raise
    except Exception as exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/lead-assessment/{cycle_id}", response_model=StageInfoResponse)
def get_lead_assessment_stage(cycle_id: int, db: Session = Depends(get_db)):
    try:
        return fetch_lead_assessment_stage_info(cycle_id, db)
    except HTTPException:
        raise
    except Exception as exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
