from pydantic import BaseModel
from datetime import date
from typing import Literal, List


class Stages(BaseModel):
    stage_id: int
    stage_name: str
    start_date_of_stage: date
    end_date_of_stage: date


class Parameters(BaseModel):
    parameter_id: int
    parameter_title: str
    helptext: str
    cycle_id: int
    applicable_to_employee: bool
    applicable_to_lead: bool
    is_fixed_parameter: bool


class GetAppraisalCycleResponse(BaseModel):
    cycle_id: int
    cycle_name: str
    description: str
    status: Literal["active", "inactive", "completed"]
    start_date_of_cycle: date
    end_date_of_cycle: date
    stages: List[Stages]
    parameters: List[Parameters]
