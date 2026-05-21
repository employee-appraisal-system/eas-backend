from pydantic import BaseModel
from typing import List, Optional


class Stage(BaseModel):
    name: str
    stage_id: Optional[int] = None
    startDate: str
    endDate: str


class Parameter(BaseModel):
    name: str
    parameter_id: Optional[int] = None
    helptext: str
    employee: bool
    teamLead: bool
    fixed: bool


class CycleUpdate(BaseModel):
    cycle_name: str
    description: str
    status: str
    start_date_of_cycle: str
    end_date_of_cycle: str
    parameters: List[Parameter]
    stages: List[Stage]
