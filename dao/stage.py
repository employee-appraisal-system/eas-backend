from sqlalchemy.orm import Session
from models.stages import Stage
from models.appraisal_cycle import AppraisalCycle
from dao.appraisal_cycle import get_cycle_by_id
from schema.stage import StageCreate
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError


# Fetch all stages
def get_all_stages(db: Session):
    try:
        return db.query(Stage).all()
    except SQLAlchemyError as e:
        raise Exception(f"Database query failed while fetching stages: {str(e)}")


#   Fetch stages by cycle ID
def create_stage(db: Session, stage_data: StageCreate):
    try:
        cycle = get_cycle_by_id(db, stage_data.cycle_id)

        if not cycle:
            raise HTTPException(
                status_code=404,
                detail=f"Appraisal Cycle with ID {stage_data.cycle_id} not found",
            )

        # Validate if stage dates are within cycle dates
        if not (
            cycle.start_date_of_cycle
            <= stage_data.start_date_of_stage
            <= cycle.end_date_of_cycle
        ):
            raise HTTPException(
                status_code=400,
                detail="Stage start date must be within the cycle start and end dates",
            )

        if not (
            cycle.start_date_of_cycle
            <= stage_data.end_date_of_stage
            <= cycle.end_date_of_cycle
        ):
            raise HTTPException(
                status_code=400,
                detail="Stage end date must be within the cycle start and end dates",
            )

        if stage_data.start_date_of_stage > stage_data.end_date_of_stage:
            raise HTTPException(
                status_code=400, detail="Stage start date cannot be after end date"
            )

        new_stage = Stage(**stage_data.dict())
        db.add(new_stage)
        db.commit()
        db.refresh(new_stage)
        return new_stage

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


#   Fetch stages by cycle ID
def get_self_assessment_stage_by_cycle_id(db: Session, cycle_id: int):
    try:
        stage = (
            db.query(Stage)
            .filter(
                Stage.cycle_id == cycle_id, Stage.stage_name.ilike("Self Assessment")
            )
            .first()
        )
        return stage
    except Exception as exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


#   Fetch lead assessment stages by cycle ID
def get_lead_assessment_stage_by_cycle_id(db: Session, cycle_id: int):
    try:
        stage = (
            db.query(Stage)
            .filter(
                Stage.cycle_id == cycle_id, Stage.stage_name.ilike("Lead Assessment")
            )
            .first()
        )
        return stage
    except Exception as exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
