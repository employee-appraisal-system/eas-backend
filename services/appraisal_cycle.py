from fastapi import HTTPException
from sqlalchemy.orm import Session
from dao.appraisal_cycle import (
    create_cycle,
    get_all_cycles,
    get_cycle_by_id,
    get_all_cycles_with_stages,
    delete_cycle,
    fetch_cycle_status_by_id,
    get_completed_and_lead_assessment_active_cycles,
    get_completed_and_self_assessment_active_cycles,
)
from schema.appraisal_cycle_pydantic import AppraisalCycleCreate


# To create new cycle
def add_new_cycle(db: Session, cycle_data: AppraisalCycleCreate):
    try:
        return create_cycle(db, cycle_data)
    except HTTPException:
        raise


# To get list of all cycles
def fetch_all_cycles(db: Session):
    try:
        return get_all_cycles(db)
    except HTTPException:
        raise


# To fetch the cycles by cycle ID
def fetch_cycle_by_id(db: Session, cycle_id: int):
    try:
        return get_cycle_by_id(db, cycle_id)
    except HTTPException:
        raise


# To fetch the cycles along with the stages
def fetch_all_cycles_with_stages(db: Session):
    try:
        return get_all_cycles_with_stages(db)
    except HTTPException:
        raise


# To delete the cycle
def delete_appraisal_cycle(db: Session, cycle_id: int):
    try:
        return delete_cycle(db, cycle_id)
    except HTTPException:
        raise


# To get the cycle status
def get_cycle_status_service(db: Session, cycle_id: int):
    try:
        cycle = fetch_cycle_status_by_id(db, cycle_id)
        return {"cycle_id": cycle.cycle_id, "status": cycle.status}
    except HTTPException:
        raise


# To get the completed cycles
def get_completed_cycles(db: Session):
    try:
        return get_completed_and_lead_assessment_active_cycles(db)
    except HTTPException:
        raise


# To get the completed cycles and active cycles for which the self assesment cycle is active
def get_filtered_cycles(db: Session):
    try:
        return get_completed_and_self_assessment_active_cycles(db)
    except HTTPException:
        raise
