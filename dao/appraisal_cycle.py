from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from collections import defaultdict
from sqlalchemy import or_, and_
from models.appraisal_cycle import AppraisalCycle
from models.stages import Stage
from models.parameters import Parameter
from schema.appraisal_cycle_pydantic import (
    AppraisalCycleCreate,
    StageResponse,
    AppraisalCycleResponseWithStages,
)


# create a new appraisal cycle
def create_cycle(db: Session, cycle_data: AppraisalCycleCreate):
    """'
    Create a new appraisal cycle in the database.
    Args:
        db: Database session
        cycle_data:object containing cycle details
    Returns:
        Newly created AppraisalCycle object
    """
    try:
        new_cycle = AppraisalCycle(
            cycle_name=cycle_data.cycle_name,
            description=cycle_data.description,
            status=cycle_data.status,
            start_date_of_cycle=cycle_data.start_date_of_cycle,
            end_date_of_cycle=cycle_data.end_date_of_cycle,
        )
        db.add(new_cycle)  # Add the new cycle
        db.commit()
        db.refresh(new_cycle)
        return new_cycle
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Database error while creating cycle."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# get all appraisal cycles
def get_all_cycles(db: Session):
    """
    Fetch all appraisal cycles from the database.
    Args:
        db: Database session
        Returns:
            List of all AppraisalCycle objects
    """
    try:
        return db.query(AppraisalCycle).all()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Database error while fetching all cycles."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get cycle by id
def get_cycle_by_id(db: Session, cycle_id: int):
    """
    Fetch a specific appraisal cycle by its ID.
    Args:
        db: Database session
        cycle_id: ID of the appraisal cycle
    Returns: AppraisalCycle object if found, else None
    """
    try:
        return (
            db.query(AppraisalCycle).filter(AppraisalCycle.cycle_id == cycle_id).first()
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Database error while fetching cycle by ID."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get all cycles with stages
def get_all_cycles_with_stages(db: Session):
    """
    Fetch all appraisal cycles along with their stages.
    Args:
        db: Database session
    Returns:
        List of Appraisal Cycle objects with corresponding stages

    """
    try:
        cycles = (
            db.query(
                AppraisalCycle.cycle_id,
                AppraisalCycle.cycle_name,
                AppraisalCycle.description,
                AppraisalCycle.status,
                AppraisalCycle.start_date_of_cycle,
                AppraisalCycle.end_date_of_cycle,
                Stage.stage_name,
                Stage.start_date_of_stage,
                Stage.end_date_of_stage,
            )
            .join(Stage, AppraisalCycle.cycle_id == Stage.cycle_id, isouter=True)
            .all()
        )

        cycle_dict = defaultdict(
            lambda: {
                "cycle_id": None,
                "cycle_name": None,
                "description": None,
                "status": None,
                "start_date_of_cycle": None,
                "end_date_of_cycle": None,
                "stages": [],
            }
        )

        for cycle in cycles:
            cycle_data = cycle_dict[cycle.cycle_id]
            if cycle_data["cycle_id"] is None:
                cycle_data.update(
                    {
                        "cycle_id": cycle.cycle_id,
                        "cycle_name": cycle.cycle_name,
                        "description": cycle.description,
                        "status": cycle.status,
                        "start_date_of_cycle": cycle.start_date_of_cycle,
                        "end_date_of_cycle": cycle.end_date_of_cycle,
                        "stages": [],
                    }
                )

            if cycle.stage_name:
                cycle_data["stages"].append(
                    StageResponse(
                        stage_name=cycle.stage_name,
                        start_date_of_stage=cycle.start_date_of_stage,
                        end_date_of_stage=cycle.end_date_of_stage,
                    )
                )

        return [
            AppraisalCycleResponseWithStages(**cycle_data)
            for cycle_data in cycle_dict.values()
        ]
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Database error while fetching cycles with stages."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# delte cycle by id
def delete_cycle(db: Session, cycle_id: int):
    """'
    Delete an appraisal cycle by its ID.
    Args:
        db: Database session
        cycle_id: ID of the appraisal cycle to delete
    Returns:
        Success message if deletion is successful
    """
    try:
        cycle = (
            db.query(AppraisalCycle).filter(AppraisalCycle.cycle_id == cycle_id).first()
        )  # Fetch the cycle

        if not cycle:
            raise HTTPException(status_code=404, detail="Cycle not found")
        # Check if the cycle is active or completed
        if cycle.status in ["active", "completed"]:
            raise HTTPException(
                status_code=400, detail="Cannot delete an active or completed cycle."
            )

        db.query(Stage).filter(Stage.cycle_id == cycle_id).delete()
        db.query(Parameter).filter(Parameter.cycle_id == cycle_id).delete()

        db.delete(cycle)
        db.commit()

        return {"message": "Cycle and related stages deleted successfully"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Database error while deleting cycle."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# get cycle status by id
def fetch_cycle_status_by_id(db: Session, cycle_id: int):
    """
    Fetch the status of a specific appraisal cycle by its ID.
    Args:
        db: Database session
        cycle_id: ID of the appraisal cycle
    Returns:
        AppraisalCycle object if found, else None
    """
    try:
        cycle = (
            db.query(AppraisalCycle).filter(AppraisalCycle.cycle_id == cycle_id).first()
        )
        if not cycle:
            raise HTTPException(status_code=404, detail="Appraisal cycle not found")
        return cycle
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching cycle status.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get completed and active cycles for the lead assessment report
def get_completed_and_lead_assessment_active_cycles(db: Session):
    """
    Fetch all completed cycles and current active cycles for the lead assessment report.
    Args:
        db: Database session
    Returns:
        List of AppraisalCycle objects
    """
    try:
        return (
            db.query(AppraisalCycle)
            .filter(AppraisalCycle.status.in_(["completed", "active"]))
            .all()
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching lead assessment report cycles.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# get completed and self assessment active cycles
def get_completed_and_self_assessment_active_cycles(db: Session):
    """
    Fetch all completed cycles and active cycles for which the "Self Assessment" stage is active.
    Args:
        db: Database session
        Returns:
            List of AppraisalCycle objects
    """
    try:
        return (
            db.query(AppraisalCycle)
            .join(Stage, AppraisalCycle.cycle_id == Stage.cycle_id)
            .filter(
                or_(
                    AppraisalCycle.status == "completed",
                    and_(
                        AppraisalCycle.status == "active",
                        Stage.stage_name == "Self Assessment",
                        or_(Stage.is_active == True, Stage.is_completed == True),
                    ),
                )
            )
            .distinct()
            .all()
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching self assessment cycles.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
