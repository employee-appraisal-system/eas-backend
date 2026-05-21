from pydantic import BaseModel
from datetime import date
from typing import Literal, List


class AppraisalCycleCreate(BaseModel):
    cycle_name: str
    description: str
    status: Literal[
        "active", "inactive", "completed"
    ]  # Restricts status to these values
    start_date_of_cycle: date
    end_date_of_cycle: date


class AppraisalCycleResponse(AppraisalCycleCreate):
    cycle_id: int

    class Config:
        orm_mode = True


class StageResponse(BaseModel):
    stage_name: str
    start_date_of_stage: date
    end_date_of_stage: date


class AppraisalCycleResponseWithStages(BaseModel):
    cycle_id: int
    cycle_name: str
    description: str
    status: str
    start_date_of_cycle: date
    end_date_of_cycle: date
    stages: List[StageResponse]
